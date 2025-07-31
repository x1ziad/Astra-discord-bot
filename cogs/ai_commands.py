import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional, List
import sys
import os

# Ensure proper import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_chat import AIChatHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("astra.ai_commands")


class AICommands(commands.Cog):
    """Commands for interacting with Astra's AI capabilities."""

    def __init__(self, bot):
        self.bot = bot
        self.ai_handler = AIChatHandler()
        self.dedicated_channels = self._load_dedicated_channels()
        logger.info("AI Commands cog initialized")

    def _load_dedicated_channels(self) -> List[int]:
        """Load dedicated AI channels from config."""
        return self.ai_handler.config.get("trigger_modes", {}).get(
            "dedicated_channels", []
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages that should trigger the AI."""
        # Ignore messages from bots to prevent loops
        if message.author.bot:
            return

        # Get configuration
        trigger_modes = self.ai_handler.config.get("trigger_modes", {})

        should_respond = False

        # Check if it's a direct message
        if trigger_modes.get("dm", True) and isinstance(
            message.channel, discord.DMChannel
        ):
            should_respond = True

        # Check if the bot was mentioned
        elif trigger_modes.get("mention", True) and self.bot.user in message.mentions:
            should_respond = True

        # Check if it's in a dedicated AI channel
        elif message.channel.id in self._load_dedicated_channels():
            should_respond = True

        # Check if message contains the trigger keyword
        elif (
            trigger_modes.get("keyword")
            and trigger_modes.get("keyword").lower() in message.content.lower()
        ):
            should_respond = True

        if should_respond:
            await self.process_ai_message(message)

    async def process_ai_message(self, message):
        """Process a message that should get an AI response."""
        # Add typing indicator to show the bot is "thinking"
        async with message.channel.typing():
            # Add the user's message to history
            await self.ai_handler.add_message_to_history(
                message.channel.id,
                message.author.id,
                str(message.author),
                message.content,
            )

            # Get AI response
            response = await self.ai_handler.get_ai_response(message.channel.id)

            # Add bot's response to history
            await self.ai_handler.add_message_to_history(
                message.channel.id,
                self.bot.user.id,
                str(self.bot.user),
                response,
                is_bot=True,
            )

            # Send the response
            await message.reply(response)

    @app_commands.command(name="ai", description="Ask Astra's AI something directly")
    @app_commands.describe(question="The question or message for Astra")
    async def ai_command(self, interaction: discord.Interaction, question: str):
        """Command to directly ask the AI a question."""
        await interaction.response.defer(thinking=True)

        # Add the user's message to history
        await self.ai_handler.add_message_to_history(
            interaction.channel_id, interaction.user.id, str(interaction.user), question
        )

        # Get AI response
        response = await self.ai_handler.get_ai_response(interaction.channel_id)

        # Add bot's response to history
        await self.ai_handler.add_message_to_history(
            interaction.channel_id,
            self.bot.user.id,
            str(self.bot.user),
            response,
            is_bot=True,
        )

        await interaction.followup.send(response)

    @app_commands.command(
        name="setpersonality", description="Change Astra's personality"
    )
    @app_commands.describe(personality="The personality profile to use")
    async def set_personality(self, interaction: discord.Interaction, personality: str):
        """Command to change the AI's personality."""
        success = await self.ai_handler.set_personality(personality)

        if success:
            await interaction.response.send_message(
                f"✅ Personality changed to: {personality}"
            )
        else:
            personalities = self.ai_handler.list_personalities()
            await interaction.response.send_message(
                f"❌ Personality '{personality}' not found. Available options: {', '.join(personalities)}"
            )

    @app_commands.command(
        name="personalities", description="List available personality profiles"
    )
    async def list_personalities(self, interaction: discord.Interaction):
        """List all available personality profiles."""
        personalities = self.ai_handler.list_personalities()

        if personalities:
            current = self.ai_handler.config.get("default_personality", "assistant")
            embed = discord.Embed(
                title="Available Personality Profiles", color=discord.Color.blue()
            )

            for p in personalities:
                try:
                    profile = self.ai_handler.load_personality(p)
                    description = profile.get("description", "No description available")
                    name = f"{p} {'(current)' if p == current else ''}"
                    embed.add_field(name=name, value=description, inline=False)
                except:
                    embed.add_field(
                        name=p, value="Error loading profile details", inline=False
                    )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No personality profiles found.")

    @app_commands.command(name="aiconfig", description="Configure AI behavior")
    @app_commands.describe(
        provider="AI provider to use (openai, anthropic, cohere, mistral, local)",
        temperature="Response randomness (0.0-2.0)",
        max_tokens="Maximum response length",
    )
    async def ai_config(
        self,
        interaction: discord.Interaction,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Configure AI behavior settings."""
        changes = []

        if provider:
            valid_providers = ["openai", "anthropic", "cohere", "mistral", "local"]
            if provider in valid_providers:
                await self.ai_handler.change_provider(provider)
                changes.append(f"Provider changed to {provider}")
            else:
                return await interaction.response.send_message(
                    f"❌ Invalid provider. Options are: {', '.join(valid_providers)}"
                )

        if temperature is not None:
            if 0.0 <= temperature <= 2.0:
                self.ai_handler.config["temperature"] = temperature
                changes.append(f"Temperature set to {temperature}")
            else:
                return await interaction.response.send_message(
                    "❌ Temperature must be between 0.0 and 2.0"
                )

        if max_tokens is not None:
            if max_tokens > 0:
                self.ai_handler.config["max_tokens"] = max_tokens
                changes.append(f"Max tokens set to {max_tokens}")
            else:
                return await interaction.response.send_message(
                    "❌ Max tokens must be greater than 0"
                )

        if changes:
            self.ai_handler._save_config()
            await interaction.response.send_message(
                "✅ Configuration updated:\n- " + "\n- ".join(changes)
            )
        else:
            # Show current config
            config = self.ai_handler.config
            embed = discord.Embed(
                title="Current AI Configuration", color=discord.Color.blue()
            )
            embed.add_field(
                name="Provider", value=config.get("provider", "openai"), inline=True
            )
            embed.add_field(
                name="Personality",
                value=config.get("default_personality", "assistant"),
                inline=True,
            )
            embed.add_field(
                name="Temperature",
                value=str(config.get("temperature", 0.7)),
                inline=True,
            )
            embed.add_field(
                name="Max Tokens", value=str(config.get("max_tokens", 500)), inline=True
            )
            embed.add_field(
                name="Max History",
                value=str(config.get("max_history", 10)),
                inline=True,
            )

            await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="clearhistory", description="Clear conversation history with the AI"
    )
    async def clear_history(self, interaction: discord.Interaction):
        """Clear the AI conversation history for this channel."""
        success = await self.ai_handler.clear_history(interaction.channel_id)

        if success:
            await interaction.response.send_message("✅ Conversation history cleared.")
        else:
            await interaction.response.send_message(
                "No conversation history to clear in this channel."
            )

    @app_commands.command(name="testapi", description="Test your OpenAI API connection")
    async def test_api(self, interaction: discord.Interaction):
        """Test the OpenAI API connection."""
        await interaction.response.defer(thinking=True)

        try:
            # Test API with a simple message
            test_response = await self.ai_handler._get_openai_response(
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'API test successful!'"},
                ],
                {"temperature": 0.7, "max_tokens": 50},
            )

            embed = discord.Embed(
                title="✅ API Test Successful",
                description=f"Response: {test_response}",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ API Test Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    try:
        await bot.add_cog(AICommands(bot))
        print("✅ AI Commands cog loaded successfully")
    except Exception as e:
        print(f"❌ Error loading AI Commands cog: {e}")
