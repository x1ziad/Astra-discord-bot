import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show a list of Astra commands")
    async def help(self, interaction: discord.Interaction):
        user = interaction.user
        is_admin = interaction.user.guild_permissions.administrator

        embed = discord.Embed(
            title="🚀 Astra Bot Commands",
            description="Your sophisticated Discord companion for space exploration and community management",
            color=0x5865F2,
        )

        embed.add_field(
            name="🎮 Quiz & Games",
            value="`/quiz` - Interactive quiz\n`/leaderboard` - Quiz rankings",
            inline=False,
        )

        embed.add_field(
            name="🌌 Space & Astronomy",
            value="`/apod` - NASA Picture of the Day\n`/fact` - Random space facts\n`/meteor` - Meteor shower info",
            inline=False,
        )

        embed.add_field(
            name="🏛️ Stellaris Empire",
            value="`/empire` - Choose your empire role\n`/lore [topic]` - Stellaris lore",
            inline=False,
        )

        embed.add_field(
            name="📊 Server Stats",
            value="`/stats` - Server statistics\n`/ping` - Bot latency\n`/uptime` - Bot uptime",
            inline=False,
        )

        embed.add_field(
            name="📓 Notion Integration",
            value="`/reminders` - Upcoming events\n`/todo` - Task management",
            inline=False,
        )

        if is_admin:
            embed.add_field(
                name="🔧 Admin Tools",
                value="`/reload` - Reload specific cog\n`/shutdown` - Stop the bot",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
