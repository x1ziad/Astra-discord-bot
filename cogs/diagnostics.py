"""
AI Diagnostics Cog for Astra Bot
Provides commands to test and verify AI functionality
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from config.railway_config import (
    get_railway_config,
    get_active_ai_config,
    get_ai_provider,
)

logger = logging.getLogger("astra.diagnostics")


class DiagnosticsCog(commands.Cog):
    """AI diagnostics and testing commands"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.diagnostics")

    @app_commands.command(
        name="ai_status", description="Check AI provider and model status"
    )
    async def ai_status(self, interaction: discord.Interaction):
        """Check current AI configuration and status"""
        try:
            await interaction.response.defer()

            # Get Railway configuration
            railway_config = get_railway_config()
            ai_provider = get_ai_provider()
            ai_config = get_active_ai_config()

            embed = discord.Embed(
                title="🤖 AI System Status", color=0x00D4FF, timestamp=datetime.now(datetime.UTC)
            )

            # Provider Information
            embed.add_field(
                name="🎯 Active Provider", value=ai_provider.title(), inline=True
            )

            if ai_provider == "github_models":
                embed.add_field(
                    name="🧠 Model",
                    value=ai_config.get("model", "DeepSeek-R1-0528"),
                    inline=True,
                )
                embed.add_field(
                    name="🔑 GitHub Token",
                    value=(
                        "✅ Configured"
                        if ai_config.get("github_token")
                        else "❌ Missing"
                    ),
                    inline=True,
                )
            elif ai_provider == "openai":
                embed.add_field(
                    name="🧠 Model",
                    value=ai_config.get("model", "gpt-3.5-turbo"),
                    inline=True,
                )
                embed.add_field(
                    name="🔑 OpenAI Key",
                    value=(
                        "✅ Configured"
                        if ai_config.get("openai_api_key")
                        else "❌ Missing"
                    ),
                    inline=True,
                )

            # Configuration
            embed.add_field(
                name="🌡️ Temperature",
                value=str(ai_config.get("temperature", 0.7)),
                inline=True,
            )
            embed.add_field(
                name="📝 Max Tokens",
                value=str(ai_config.get("max_tokens", 1500)),
                inline=True,
            )

            # Check if AI cog is loaded
            ai_cog = self.bot.get_cog("AdvancedAICog")
            ai_client_status = (
                "✅ Ready"
                if ai_cog and hasattr(ai_cog, "ai_client")
                else "❌ Not Ready"
            )

            embed.add_field(name="🔧 AI Client", value=ai_client_status, inline=True)

            embed.set_footer(text="Use /ai_test to test AI functionality")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"AI status check error: {e}")
            await interaction.followup.send(
                f"❌ Error checking AI status: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="ai_test", description="Test AI with a simple prompt")
    @app_commands.describe(prompt="Test prompt for AI (optional)")
    async def ai_test(self, interaction: discord.Interaction, prompt: str = None):
        """Test AI functionality with a diagnostic prompt"""
        try:
            await interaction.response.defer()

            # Get AI cog
            ai_cog = self.bot.get_cog("AdvancedAICog")
            if not ai_cog:
                await interaction.followup.send(
                    "❌ AI system not available", ephemeral=True
                )
                return

            # Use diagnostic prompt if none provided
            test_prompt = (
                prompt
                or "Hello! Please respond with: 1) Your model name 2) Current time 3) A fun fact about space. This is a diagnostic test."
            )

            # Generate AI response
            response = await ai_cog._generate_ai_response(
                test_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🧪 AI Diagnostic Test",
                color=0x43B581,
                timestamp=datetime.now(datetime.UTC),
            )

            embed.add_field(
                name="📥 Test Prompt",
                value=test_prompt[:200] + ("..." if len(test_prompt) > 200 else ""),
                inline=False,
            )

            embed.add_field(
                name="📤 AI Response",
                value=response[:1000] + ("..." if len(response) > 1000 else ""),
                inline=False,
            )

            # Add provider info
            ai_provider = get_ai_provider()
            embed.add_field(name="🎯 Provider", value=ai_provider.title(), inline=True)

            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            embed.set_footer(text="✅ AI system is working correctly!")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"AI test error: {e}")
            embed = discord.Embed(
                title="❌ AI Test Failed",
                description=f"Error: {str(e)}",
                color=0xF04747,
                timestamp=datetime.now(datetime.UTC),
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="deepseek_verify", description="Specifically test DeepSeek R1 model"
    )
    async def deepseek_verify(self, interaction: discord.Interaction):
        """Verify DeepSeek R1 is working with specific test"""
        try:
            await interaction.response.defer()

            # Get AI cog
            ai_cog = self.bot.get_cog("AdvancedAICog")
            if not ai_cog:
                await interaction.followup.send(
                    "❌ AI system not available", ephemeral=True
                )
                return

            # DeepSeek-specific test prompt
            deepseek_prompt = """Please respond with exactly this format:
MODEL: [Your model name]
PROVIDER: [Your provider]
REASONING: [Show me your step-by-step reasoning for solving: 2+2*3]
SPACE_FACT: [One interesting fact about black holes]

This is a diagnostic test to verify DeepSeek R1 functionality."""

            # Generate AI response
            response = await ai_cog._generate_ai_response(
                deepseek_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔬 DeepSeek R1 Verification Test",
                color=0x7C3AED,
                timestamp=datetime.now(datetime.UTC),
            )

            embed.add_field(
                name="🧠 Expected Model", value="DeepSeek-R1-0528", inline=True
            )

            embed.add_field(
                name="🎯 Expected Provider", value="GitHub Models", inline=True
            )

            embed.add_field(
                name="📤 DeepSeek Response",
                value=response[:1500] + ("..." if len(response) > 1500 else ""),
                inline=False,
            )

            # Check if response indicates DeepSeek
            is_deepseek = any(
                keyword in response.lower()
                for keyword in ["deepseek", "r1", "reasoning"]
            )
            status_emoji = "✅" if is_deepseek else "⚠️"

            embed.add_field(
                name=f"{status_emoji} DeepSeek Detection",
                value=(
                    "Likely DeepSeek R1" if is_deepseek else "Cannot confirm DeepSeek"
                ),
                inline=True,
            )

            embed.set_footer(
                text="This test helps verify if DeepSeek R1 is working on Railway"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"DeepSeek verification error: {e}")
            embed = discord.Embed(
                title="❌ DeepSeek Verification Failed",
                description=f"Error: {str(e)}",
                color=0xF04747,
                timestamp=datetime.now(datetime.UTC),
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DiagnosticsCog(bot))
    logger.info("✅ DiagnosticsCog loaded successfully")
