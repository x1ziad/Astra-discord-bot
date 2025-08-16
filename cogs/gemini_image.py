"""
Gemini Image Generation Cog for Astra Bot
Discord bot cog for Google Gemini AI image generation
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional, Literal

from ai.gemini_discord_integration import get_gemini_discord
from ai.gemini_image_generator import get_gemini_generator

logger = logging.getLogger("astra.gemini_cog")


class GeminiImageCog(commands.Cog):
    """
    Gemini Image Generation Cog
    Provides Discord commands for generating images with Google Gemini AI
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.discord_interface = get_gemini_discord()
        self.generator = get_gemini_generator()
        self.logger = logging.getLogger("astra.gemini_cog")

        self.logger.info("🤖 Gemini Image Cog initialized")

    @app_commands.command(
        name="gemini-image",
        description="🎨 Generate high-quality images using Google Gemini AI",
    )
    @app_commands.describe(
        prompt="Detailed description of the image you want to generate",
        style="Art style for the image",
        size="Image dimensions and aspect ratio",
    )
    @app_commands.choices(
        style=[
            app_commands.Choice(name="🎨 Realistic", value="realistic"),
            app_commands.Choice(name="✨ Artistic", value="artistic"),
            app_commands.Choice(name="🎭 Cartoon", value="cartoon"),
            app_commands.Choice(name="🌸 Anime", value="anime"),
            app_commands.Choice(name="📸 Photographic", value="photographic"),
            app_commands.Choice(name="🎪 Abstract", value="abstract"),
            app_commands.Choice(name="📻 Vintage", value="vintage"),
        ]
    )
    @app_commands.choices(
        size=[
            app_commands.Choice(name="Square HD (1024x1024)", value="square_hd"),
            app_commands.Choice(name="Portrait (768x1024)", value="portrait"),
            app_commands.Choice(name="Landscape (1024x768)", value="landscape"),
            app_commands.Choice(name="Wide (1024x576)", value="wide"),
        ]
    )
    async def gemini_image(
        self,
        interaction: discord.Interaction,
        prompt: str,
        style: str = "realistic",
        size: str = "square_hd",
    ):
        """Generate an image using Google Gemini AI"""
        await self.discord_interface.handle_image_command(
            interaction, prompt, style, size
        )

    @app_commands.command(
        name="gemini-status",
        description="📊 Check Gemini image generation system status",
    )
    async def gemini_status(self, interaction: discord.Interaction):
        """Show Gemini image generation system status"""
        try:
            await interaction.response.defer()

            status_embed = await self.discord_interface.get_status_embed()
            await interaction.followup.send(embed=status_embed)

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            await interaction.followup.send(
                "❌ Error retrieving status information.", ephemeral=True
            )

    @app_commands.command(
        name="gemini-test", description="🧪 Test Gemini AI connection (Admin only)"
    )
    async def gemini_test(self, interaction: discord.Interaction):
        """Test Gemini AI connection"""
        try:
            # Check if user is admin
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ This command is only available to administrators.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()

            # Test connection
            test_result = await self.generator.test_connection()

            if test_result["success"]:
                embed = discord.Embed(
                    title="✅ Gemini AI Test Successful",
                    description="Connection to Google Gemini AI is working properly.",
                    color=0x27AE60,
                )
                embed.add_field(
                    name="📊 Test Results",
                    value=f"**Model:** {test_result.get('model', 'Unknown')}\n"
                    f"**Generation Time:** {test_result.get('generation_time', 0):.2f}s\n"
                    f"**Has Image Data:** {'✅' if test_result.get('has_image_data') else '❌'}",
                    inline=False,
                )
            else:
                embed = discord.Embed(
                    title="❌ Gemini AI Test Failed",
                    description=f"Error: {test_result.get('error', 'Unknown error')}",
                    color=0xE74C3C,
                )

                if "details" in test_result:
                    details = test_result["details"]
                    embed.add_field(
                        name="🔍 Details",
                        value=f"**SDK Available:** {'✅' if details.get('gemini_sdk') else '❌'}\n"
                        f"**API Key Set:** {'✅' if details.get('api_key_set') else '❌'}\n"
                        f"**Client Initialized:** {'✅' if details.get('client_initialized') else '❌'}",
                        inline=False,
                    )

            embed.set_footer(text="🤖 Google Gemini AI Test")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in test command: {e}")
            await interaction.followup.send(
                f"❌ Test failed with error: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="gemini-help", description="❓ Get help with Gemini image generation"
    )
    async def gemini_help(self, interaction: discord.Interaction):
        """Show help for Gemini image generation"""
        try:
            embed = discord.Embed(
                title="🎨 Gemini Image Generation Help",
                description="Generate stunning AI images with Google Gemini AI!",
                color=0x3498DB,
            )

            embed.add_field(
                name="🚀 Quick Start",
                value="`/gemini-image prompt:a beautiful sunset over mountains`",
                inline=False,
            )

            embed.add_field(
                name="🎨 Available Styles",
                value="• **Realistic** - Photorealistic images\n"
                "• **Artistic** - Creative and artistic style\n"
                "• **Cartoon** - Fun cartoon-style images\n"
                "• **Anime** - Japanese animation style\n"
                "• **Photographic** - Professional photography\n"
                "• **Abstract** - Abstract and modern art\n"
                "• **Vintage** - Retro and nostalgic style",
                inline=True,
            )

            embed.add_field(
                name="📐 Available Sizes",
                value="• **Square HD** - 1024x1024 (default)\n"
                "• **Portrait** - 768x1024\n"
                "• **Landscape** - 1024x768\n"
                "• **Wide** - 1024x576",
                inline=True,
            )

            embed.add_field(
                name="✨ Pro Tips",
                value="• Be specific and descriptive\n"
                "• Include details about lighting, mood, colors\n"
                "• Mention camera settings for photographic style\n"
                "• Experiment with different styles!\n"
                "• Use artistic terms for better results",
                inline=False,
            )

            embed.add_field(
                name="📍 Permissions",
                value=f"• **Regular Users:** <#{self.discord_interface.permissions.default_channel_id}> only\n"
                "• **Mods/Admins:** Any channel",
                inline=True,
            )

            embed.add_field(
                name="⏰ Rate Limits",
                value="• **Users:** 10/hour, 50/day\n"
                "• **Mods:** 50/hour, 200/day\n"
                "• **Admins:** 100/hour, 500/day",
                inline=True,
            )

            embed.add_field(
                name="🛠️ Other Commands",
                value="`/gemini-status` - Check system status\n"
                "`/gemini-test` - Test connection (Admin)\n"
                "`/gemini-help` - Show this help",
                inline=False,
            )

            embed.set_footer(text="🤖 Powered by Google Gemini AI • Use responsibly!")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                "❌ Error showing help information.", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the cog is ready"""
        self.logger.info("🤖 Gemini Image Cog is ready!")

        # Log availability status
        if self.generator.is_available():
            self.logger.info("✅ Gemini image generation is available")
        else:
            self.logger.warning(
                "❌ Gemini image generation is NOT available - check configuration"
            )


async def setup(bot: commands.Bot):
    """Setup function for the cog"""
    await bot.add_cog(GeminiImageCog(bot))
    logger.info("🤖 Gemini Image Cog loaded successfully")
