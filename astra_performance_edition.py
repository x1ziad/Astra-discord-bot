"""
🚀 ASTRABOT PERFORMANCE EDITION
Combines streamlined core with selective performance optimizations
Best of both worlds: Clean code + Performance where it matters

Based on successful streamlined system with targeted optimizations
"""

import asyncio
import logging
import os
import sys
import platform
import discord
from discord.ext import commands

# Performance optimizations (selective)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    UVLOOP_AVAILABLE = True
    print("⚡ uvloop acceleration enabled")
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import orjson as json
    JSON_AVAILABLE = True
    print("🚀 orjson fast JSON enabled") 
except ImportError:
    import json
    JSON_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

# Import our proven streamlined core system
from core import startup_core

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/astra.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("astra.performance")

class AstraBotPerformance(commands.Bot):
    """Performance-optimized AstraBot using proven streamlined core"""
    
    def __init__(self):
        # Optimized bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True,
            # Performance optimizations
            max_messages=1000,  # Limit message cache
            chunk_guilds_at_startup=False,  # Faster startup
            member_cache_flags=discord.MemberCacheFlags.none()  # Reduce memory
        )
        
        self.core_system = None
        self.start_time = asyncio.get_event_loop().time()
        
        # Performance metrics (lightweight)
        self.stats = {
            'messages_processed': 0,
            'ai_responses': 0,
            'menu_interactions': 0,
            'moderation_actions': 0
        }
        
    async def get_prefix(self, message):
        """Optimized dynamic prefix"""
        # Cache-friendly prefix resolution
        prefixes = [f'<@{self.user.id}> ', f'<@!{self.user.id}> ', 'astra ', 'hey astra ', '!']
        return commands.when_mentioned_or(*prefixes)(self, message)
        
    async def setup_hook(self):
        """Optimized setup with proven core system"""
        logger.info("🔧 Setting up AstraBot Performance Edition...")
        
        try:
            # Initialize our proven streamlined core system
            self.core_system = await startup_core(self)
            
            # Load only essential cogs (performance-critical)
            essential_cogs = [
                'cogs.help',      # Keep help system
                'cogs.utilities', # Keep basic utilities  
            ]
            
            for cog in essential_cogs:
                try:
                    await self.load_extension(cog)
                    logger.info(f"✅ Loaded {cog}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not load {cog}: {e}")
                    
            logger.info("🚀 AstraBot Performance Edition ready!")
            
        except Exception as e:
            logger.error(f"💥 Setup failed: {e}")
            await self.close()
            
    async def on_ready(self):
        """Optimized ready event"""
        uptime = asyncio.get_event_loop().time() - self.start_time
        
        logger.info("🚀 AstraBot Performance Edition Online!")
        logger.info(f"📊 Startup time: {uptime:.2f}s")
        logger.info(f"🏰 Serving {len(self.guilds)} guilds with {len(self.users)} users")
        
        if UVLOOP_AVAILABLE:
            logger.info("⚡ uvloop acceleration active")
        if JSON_AVAILABLE:
            logger.info("🚀 orjson fast JSON active")
            
        # Optimized bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="conversations • Mention me to chat!"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        
    async def on_message(self, message):
        """Performance-optimized message handling"""
        if message.author.bot:
            return
            
        # Increment counter (lightweight)
        self.stats['messages_processed'] += 1
        
        # Let core system handle the message
        # (This bypasses the default command processing for better performance)
        
    async def close(self):
        """Optimized graceful shutdown"""
        logger.info("🔄 Shutting down AstraBot Performance Edition...")
        
        if self.core_system:
            await self.core_system.shutdown()
            
        await super().close()
        
        uptime = asyncio.get_event_loop().time() - self.start_time
        logger.info(f"⏱️  Total uptime: {uptime:.2f}s")
        logger.info(f"📊 Messages processed: {self.stats['messages_processed']}")
        logger.info("✅ Performance Edition shutdown complete")

async def main():
    """Optimized main function"""
    # Load token from environment (.env file) or config
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                token = config.get('discord', {}).get('token')
        except FileNotFoundError:
            logger.error("❌ No config.json found and DISCORD_TOKEN not set")
            return
            
    if not token or token == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.error("❌ Discord token not found or is placeholder!")
        logger.error("   Please set DISCORD_TOKEN in .env file or config.json")
        return
        
    logger.info("🔑 Discord token loaded successfully!")
    
    # Performance info
    logger.info("=" * 60)
    logger.info("⚡ ASTRABOT PERFORMANCE EDITION")
    logger.info(f"🚀 Python: {platform.python_version()}")
    logger.info(f"📦 Discord.py: {discord.__version__}")
    logger.info(f"⚡ uvloop: {'✅ Active' if UVLOOP_AVAILABLE else '❌ Not available'}")
    logger.info(f"🚀 orjson: {'✅ Active' if JSON_AVAILABLE else '❌ Using standard json'}")
    logger.info("=" * 60)
        
    # Create and run optimized bot
    bot = AstraBotPerformance()
    
    try:
        logger.info("🚀 Starting AstraBot Performance Edition...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    # Run the optimized bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)