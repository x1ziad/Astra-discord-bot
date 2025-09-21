import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger("astra.help")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show a list of Astra commands")
    @app_commands.describe(category="Specific command category to show")
    async def help(self, interaction: discord.Interaction, category: str = None):
        """Show help information with error handling and permission checks"""
        try:
            user = interaction.user
            is_admin = user.guild_permissions.administrator if interaction.guild else False

            embed = discord.Embed(
                title="🚀 Astra Bot Commands",
                description="Your sophisticated Discord companion for space exploration and community management",
                color=0x5865F2,
            )

            # Core AI Features
            embed.add_field(
                name="🤖 AI Features",
                value="`/chat` - Chat with Astra AI\n`/analyze` - AI text analysis\n`/summarize` - Summarize content\n`/translate` - Translate text",
                inline=False,
            )

            # Entertainment & Games
            embed.add_field(
                name="🎮 Entertainment",
                value="`/quiz` - Interactive quiz\n`/leaderboard` - Quiz rankings\n`/fact` - Random space facts",
                inline=False,
            )

            # Space & Science
            embed.add_field(
                name="🌌 Space & Science",
                value="`/apod` - NASA Picture of the Day\n`/meteor` - Meteor shower info\n`/space` - Space exploration commands",
                inline=False,
            )

            # Server Management
            embed.add_field(
                name="📊 Server Tools",
                value="`/stats` - Server statistics\n`/ping` - Bot latency\n`/status` - Bot status info",
                inline=False,
            )

            # Utility Commands
            embed.add_field(
                name="� Utilities",
                value="`/roles` - Role management\n`/utilities` - General utilities\n`/nexus` - Advanced diagnostics",
                inline=False,
            )

            # Admin Commands (only show to admins)
            if is_admin:
                embed.add_field(
                    name="⚙️ Admin Commands",
                    value="`/admin` - Administrative controls\n`/config` - Bot configuration\n`/reload` - Reload extensions",
                    inline=False,
                )

            # Set thumbnail and footer
            if self.bot.user and self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            
            embed.set_footer(text=f"Astra Bot • {len(self.bot.guilds)} servers • Use /help [category] for details")

            # Send the help message
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Help command used by {user} ({user.id})")

        except discord.InteractionResponse as e:
            # Handle case where interaction was already responded to
            logger.error(f"Interaction already responded to: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Error displaying help information", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Help command error: {e}")
            # Only respond if we haven't already
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Error displaying help: {str(e)}", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Error displaying help: {str(e)}", ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(Help(bot))
