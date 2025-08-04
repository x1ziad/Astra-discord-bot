"""
Bot Setup and Invitation Commands
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.bot_invite import generate_bot_invite_url, get_full_permissions
from config.config_manager import config_manager

class BotSetup(commands.Cog):
    """Commands for bot setup and invitation management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
    
    @app_commands.command(
        name="invite",
        description="Get an invitation link to add this bot to other servers"
    )
    async def invite_command(self, interaction: discord.Interaction):
        """Generate bot invitation URL"""
        
        # Get bot's client ID
        client_id = str(self.bot.user.id)
        
        # Generate invitation URLs
        full_url = generate_bot_invite_url(client_id, get_full_permissions())
        
        embed = discord.Embed(
            title="🤖 Invite Astra to Your Server!",
            description="Use the link below to add Astra to other Discord servers.",
            color=config_manager.get_color("success")
        )
        
        embed.add_field(
            name="🔗 Invitation Link",
            value=f"[Click here to invite Astra]({full_url})",
            inline=False
        )
        
        embed.add_field(
            name="✅ What you'll get:",
            value="• Advanced AI capabilities\n"
                  "• Space exploration commands\n"
                  "• Server analytics and management\n"
                  "• Quiz and interactive features\n"
                  "• Notion integration\n"
                  "• And much more!",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Required Permissions:",
            value="• Send Messages & Embed Links\n"
                  "• Use Slash Commands\n"
                  "• Manage Messages (for moderation)\n"
                  "• Read Message History\n"
                  "• Add Reactions",
            inline=False
        )
        
        embed.add_field(
            name="💡 Setup Instructions:",
            value="1. Click the invitation link above\n"
                  "2. Select your server\n"
                  "3. Review permissions\n"
                  "4. Click 'Authorize'\n"
                  "5. Use `/ping` to test the bot",
            inline=False
        )
        
        embed.set_footer(
            text="Need help? Contact the bot owner or check the documentation."
        )
        
        # Add share buttons as components
        view = discord.ui.View()
        
        # Direct link button
        link_button = discord.ui.Button(
            label="Invite Astra",
            style=discord.ButtonStyle.link,
            url=full_url,
            emoji="🤖"
        )
        view.add_item(link_button)
        
        # Support server button (if configured)
        support_server = config_manager.get_setting("support_server_invite")
        if support_server:
            support_button = discord.ui.Button(
                label="Support Server",
                style=discord.ButtonStyle.link,
                url=support_server,
                emoji="❓"
            )
            view.add_item(support_button)
        
        await interaction.response.send_message(embed=embed, view=view)
        
        self.logger.info(f"Invitation link requested by {interaction.user} in {interaction.guild}")
    
    @app_commands.command(
        name="setup",
        description="Get setup information for server administrators"
    )
    async def setup_command(self, interaction: discord.Interaction):
        """Provide setup information for server admins"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ This command requires 'Manage Server' permission.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="⚙️ Astra Bot Setup Guide",
            description="Welcome! Here's how to get the most out of Astra.",
            color=config_manager.get_color("info")
        )
        
        embed.add_field(
            name="🚀 Quick Start:",
            value="• Use `/ping` to test the bot\n"
                  "• Try `/space fact` for a space fact\n"
                  "• Use `/help` to see all commands\n"
                  "• Configure with `/config` (coming soon)",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Configuration:",
            value="• Set custom prefixes per server\n"
                  "• Enable/disable specific features\n"
                  "• Configure AI personality\n"
                  "• Set up automated moderation",
            inline=False
        )
        
        embed.add_field(
            name="🌟 Key Features:",
            value="• `/space apod` - NASA Astronomy Picture\n"
                  "• `/quiz start` - Interactive quizzes\n"
                  "• `/stats server` - Server analytics\n"
                  "• AI chat capabilities\n"
                  "• Role management tools",
            inline=False
        )
        
        embed.add_field(
            name="❓ Need Help?",
            value="• Use `/help [command]` for specific help\n"
                  "• Check the documentation\n"
                  "• Join our support server\n"
                  "• Report issues to bot developers",
            inline=False
        )
        
        embed.set_footer(
            text=f"Astra v{config_manager.get_bot_config().version} • Ready to explore the cosmos!"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BotSetup(bot))
