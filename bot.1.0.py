import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime

## we'll later add to the config.json file to moderate the bot use for specifi guilds and roles
# This is a placeholder for the config file, which can be used to store settings like admin roles, guild IDs, etc.
# For now, we will use environment variables for sensitive data like the bot token.

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,  # We'll create a custom help command
    case_insensitive=True,
)

# Store bot start time for uptime tracking
bot.start_time = datetime.utcnow()

# Define your extensions here
extensions = [
    "cogs.quiz",
    "cogs.roles",
    "cogs.space",
    "cogs.help",
    "cogs.notion",
    "cogs.stats",
]


async def load_extensions():
    """Load all cogs with proper error handling"""
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"✅ Loaded {ext}")
        except FileNotFoundError:
            logger.warning(f"⚠️ {ext}.py not found - skipping")
        except Exception as e:
            logger.error(f"❌ Failed to load {ext}: {e}")


@bot.event
async def on_ready():
    """Bot startup event"""
    logger.info(f"🚀 Astra is online as {bot.user}")
    logger.info(f"🌐 Connected to {len(bot.guilds)} guild(s)")
    logger.info(f"👥 Serving {len(set(bot.get_all_members()))} unique users")

    # Load extensions
    await load_extensions()

    # Set bot activity
    activity = discord.Activity(
        type=discord.ActivityType.watching, name="the cosmos | !help"
    )
    await bot.change_presence(activity=activity)

    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Slash commands synced: {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"❌ Failed to sync slash commands: {e}")

    logger.info("🎯 All systems operational!")


@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"The command `{ctx.invoked_with}` doesn't exist. Use `!help` to see available commands.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Insufficient Permissions",
            description="You don't have permission to use this command.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
            color=0xFF9900,
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        logger.error(f"Unhandled error in {ctx.command}: {error}")


@bot.command(name="help")
async def help_command(ctx):
    """Custom help command"""
    embed = discord.Embed(
        title="🚀 Astra Bot Commands",
        description="Your sophisticated Discord companion for space exploration and community management",
        color=0x5865F2,
    )

    embed.add_field(
        name="🎮 Quiz & Games",
        value="`!quiz` - Interactive space/Stellaris quiz\n`!leaderboard` - View quiz rankings",
        inline=False,
    )

    embed.add_field(
        name="🌌 Space & Astronomy",
        value="`!apod` - NASA's Astronomy Picture of the Day\n`!fact` - Random space facts\n`!meteor` - Meteor shower info",
        inline=False,
    )

    embed.add_field(
        name="🏛️ Stellaris Empire",
        value="`!empire` - Choose your empire role\n`!lore [topic]` - Stellaris lore",
        inline=False,
    )

    embed.add_field(
        name="📊 Server Stats",
        value="`!stats` - Server statistics\n`!ping` - Bot latency\n`!uptime` - Bot uptime",
        inline=False,
    )

    embed.add_field(
        name="📓 Notion Integration",
        value="`!reminders` - Upcoming events\n`!todo` - Task management",
        inline=False,
    )

    embed.set_footer(text="🌟 Astra Bot - Exploring the cosmos together")

    await ctx.send(embed=embed)


@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload_cog(ctx, cog_name: str):
    """Reload a specific cog (Admin only)"""
    try:
        await bot.reload_extension(f"cogs.{cog_name}")
        embed = discord.Embed(
            title="✅ Cog Reloaded",
            description=f"Successfully reloaded `{cog_name}`",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Reload Failed",
            description=f"Failed to reload `{cog_name}`: {str(e)}",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)


if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ DISCORD_TOKEN not found in environment variables!")
        exit(1)

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token!")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
