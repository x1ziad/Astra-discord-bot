import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger("astra.help")


class Help(commands.Cog):
    """Enhanced Help System - Redirects to AI-Powered Nexus Help"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help", 
        description="🧠 AI-Powered Help System - Get intelligent assistance and feature overview"
    )
    @app_commands.describe(
        category="Specific category (ai, server, space, admin, utilities)",
        detailed="Enable AI-generated detailed explanations"
    )
    async def help(
        self, 
        interaction: discord.Interaction, 
        category: Optional[str] = None,
        detailed: Optional[bool] = False
    ):
        """Enhanced help system with AI-powered explanations and self-awareness"""
        try:
            # Check if Nexus cog is available
            nexus_cog = self.bot.get_cog("nexus")
            
            if nexus_cog and hasattr(nexus_cog, 'nexus_help'):
                # Redirect to the enhanced Nexus help system
                await nexus_cog.nexus_help(interaction, category, detailed)
                logger.info(f"Help redirected to Nexus system by {interaction.user} ({interaction.user.id})")
                return
            
            # Fallback to basic help if Nexus is unavailable
            await self._fallback_help(interaction, category)
            
        except Exception as e:
            logger.error(f"Help system error: {e}")
            await self._emergency_help(interaction)

    async def _fallback_help(self, interaction: discord.Interaction, category: Optional[str]):
        """Fallback help system with improved AI awareness"""
        embed = discord.Embed(
            title="🌌 Astra Help System",
            description="**AI-Powered Discord Companion**\n"
                       "Advanced features for server management, space exploration, and AI assistance.\n\n"
                       "⚠️ Enhanced AI help system temporarily unavailable - using fallback mode.",
            color=0x3498DB,
        )

        # Core features with better organization
        features = {
            "🤖 AI Systems": {
                "value": "`/ai_companion` - Advanced AI chat\n"
                        "`/advanced_ai` - AI analysis tools\n"
                        "`/ai_moderation` - Smart moderation",
                "note": "Multi-provider AI with intelligent fallback"
            },
            "�️ Server Management": {
                "value": "`/enhanced_server_management` - Complete server tools\n"
                        "`/admin` - Administrative controls\n"
                        "`/roles` - Role management system",
                "note": "Comprehensive server administration"
            },
            "🌌 Space & Science": {
                "value": "`/space` - Space exploration commands\n"
                        "`/quiz` - Space knowledge quiz\n"
                        "`/stats` - Server and bot statistics",
                "note": "Real NASA data and cosmic exploration"
            },
            "�️ Advanced Diagnostics": {
                "value": "`/nexus` - System diagnostics\n"
                        "`/utilities` - General utilities\n"
                        "`/notion` - Notion integration",
                "note": "Professional-grade monitoring tools"
            }
        }

        for title, info in features.items():
            embed.add_field(
                name=f"{title}",
                value=f"{info['value']}\n*{info['note']}*",
                inline=False
            )

        # System status
        embed.add_field(
            name="📊 System Status",
            value=f"🏠 **{len(self.bot.guilds)}** servers\n"
                  f"⚡ **Multi-AI** providers active\n"
                  f"🔄 **Self-aware** help system\n"
                  f"🚀 **Enhanced** with Nexus control",
            inline=True
        )

        # Quick start guide
        embed.add_field(
            name="🚀 Quick Start",
            value="1. Try `/nexus help` for AI-powered assistance\n"
                  "2. Use `/ai_companion` for intelligent chat\n"
                  "3. Explore `/space` for cosmic adventures\n"
                  "4. Check `/nexus system` for diagnostics",
            inline=True
        )

        embed.set_footer(text="🧠 For full AI-powered help, use /nexus help when available")
        
        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _emergency_help(self, interaction: discord.Interaction):
        """Emergency help system for critical failures"""
        embed = discord.Embed(
            title="⚠️ Help System Error",
            description="The help system encountered an error. Here are basic commands:\n\n"
                       "**Core Commands:**\n"
                       "• `/nexus ping` - Check bot status\n"
                       "• `/stats server` - Server information\n"
                       "• `/ai_companion` - AI assistance\n"
                       "• `/utilities` - General tools\n\n"
                       "**For Support:** Contact bot administrator",
            color=0xFF6B6B
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
