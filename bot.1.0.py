import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
import os
from dotenv import load_dotenv

from enhanced_config import ConfigManager
from ui_components import CategorySelectView

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# Load config manager
config_manager = ConfigManager("iconfig.json")

# ---------- Slash Commands ----------


@bot.tree.command(name="help", description="Show the help menu")
@app_commands.checks.has_role("Admin")  # You can change this role name
async def slash_help(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    palette = config_manager.get(guild_id, "ui", {}).get("palette", "default")
    color = config_manager.get_color(palette)
    emoji = config_manager.get_emoji(palette, "star")

    embed = discord.Embed(
        title=f"{emoji} Astra Bot Help Menu",
        description="Choose a category from the dropdown menu below:",
        color=color,
    )
    await interaction.response.send_message(
        embed=embed, view=CategorySelectView(), ephemeral=True
    )


@bot.tree.command(name="ping", description="Check if the bot is alive")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏓 Pong! Slash command working!", ephemeral=True
    )


@bot.tree.command(
    name="invite", description="Get an invite link to add the bot to your server"
)
async def slash_invite(interaction: discord.Interaction):
    app_id = interaction.client.user.id
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions=8&scope=bot%20applications.commands"
    await interaction.response.send_message(
        f"🔗 [Click here to invite Astra]({invite_url})", ephemeral=True
    )


# ---------- Extension Loader ----------


async def load_extensions():
    extensions = [
        "cogs.quiz",
        "cogs.roles",
        "cogs.space",
        "cogs.notion",
        "cogs.stats",
        "cogs.admin",
        "cogs.user_profiles",
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"✅ Loaded extension: {ext}")
        except Exception as e:
            logger.error(f"❌ Failed to load extension {ext}: {e}")


# ---------- On Ready Event ----------


@bot.event
async def on_ready():
    await load_extensions()
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands globally.")
    except Exception as e:
        logger.error(f"❌ Failed to sync slash commands: {e}")

    logger.info(f"🟢 Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("Connected to guilds:")
    for guild in bot.guilds:
        logger.info(f" - {guild.name} ({guild.id})")


# ---------- Run Bot ----------

if TOKEN:
    bot.run(TOKEN)
else:
    logger.critical("❌ DISCORD_TOKEN not found in environment variables.")
