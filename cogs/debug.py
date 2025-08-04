"""
Debug commands and utilities for Astra
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Dict, Any

from config.config_manager import config_manager


class Debug(commands.Cog):
    """Debug and diagnostic commands"""

    def __init__(self, bot):
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

    @app_commands.command(
        name="debug", description="Check bot configuration and features"
    )
    @app_commands.default_permissions(administrator=True)
    async def debug_command(self, interaction: discord.Interaction):
        """Debug command to check feature flags and configuration"""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ This command is only available to administrators.", ephemeral=True
            )
            return

        # Get feature flags
        features = {
            "space_content": self.config.is_feature_enabled("space_content"),
            "space_content.iss_tracking": self.config.is_feature_enabled(
                "space_content.iss_tracking"
            ),
            "space_content.launch_notifications": self.config.is_feature_enabled(
                "space_content.launch_notifications"
            ),
            "quiz_system": self.config.is_feature_enabled("quiz_system"),
            "roles_management": self.config.is_feature_enabled("roles_management"),
            "notion_integration": self.config.is_feature_enabled("notion_integration"),
        }

        embed = discord.Embed(
            title="🔍 Astra Diagnostic Report",
            description="Current status of bot features and configuration:",
            color=self.config.get_color("primary"),
            timestamp=datetime.now(datetime.UTC),
        )

        # Feature flags section
        feature_status = "\n".join(
            [
                f"**{name}:** {'✅' if status else '❌'}"
                for name, status in features.items()
            ]
        )
        embed.add_field(name="🚩 Feature Flags", value=feature_status, inline=False)

        # Bot statistics
        embed.add_field(
            name="🤖 Bot Stats",
            value=f"**Servers:** {len(self.bot.guilds)}\n"
            f"**Commands:** {len(self.bot.tree.get_commands())}\n"
            f"**Cogs:** {len(self.bot.cogs)}\n"
            f"**Latency:** {self.bot.latency * 1000:.1f}ms",
            inline=True,
        )

        # Environment
        embed.add_field(
            name="🖥️ Environment",
            value=f"**Version:** {self.config.get('bot_settings.version', '1.0.0')}\n"
            f"**Debug Mode:** {'✅' if self.config.get('development.debug_mode', False) else '❌'}\n"
            f"**Command Sync:** {'✅' if self.config.get('bot_settings.command_sync_on_ready', True) else '❌'}",
            inline=True,
        )

        # Command permissions
        embed.add_field(
            name="📝 Command Permissions",
            value="Check that the bot has these permissions:\n"
            "• `applications.commands` scope\n"
            "• Send Messages\n"
            "• Embed Links\n"
            "• Use External Emojis\n"
            "• Read Message History",
            inline=False,
        )

        embed.set_footer(text=f"Requested by {interaction.user}")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Add the debug cog to the bot"""
    await bot.add_cog(Debug(bot))
