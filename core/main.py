"""
Core System Integration - Main entry point for all core functionality
Initializes and coordinates all systems - Replaces bloated main bot files
Maximum 150 lines of pure coordination code
"""

import asyncio
import logging
from typing import Dict, Optional
import discord
from discord.ext import commands

# Import all core systems
from .ai_handler import AIHandler
from .interactive_menus import InteractiveMenus
from .smart_moderation import SmartModerator
from .welcome_system import WelcomeSystem
from .event_manager import EventManager

logger = logging.getLogger("astra.core")


class CoreSystem:
    """Main core system coordinator - replaces bloated bot files"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.initialized = False

        # Initialize all core systems
        self.ai_handler = AIHandler(bot)
        self.interactive_menus = InteractiveMenus(bot)
        self.smart_moderation = SmartModerator(bot)
        self.welcome_system = WelcomeSystem(bot)
        self.event_manager = EventManager(bot)

        # Register systems with event manager
        self.event_manager.register_system("ai_handler", self.ai_handler)
        self.event_manager.register_system("interactive_menus", self.interactive_menus)
        self.event_manager.register_system("smart_moderation", self.smart_moderation)
        self.event_manager.register_system("welcome_system", self.welcome_system)

        logger.info("🚀 Core System initialized - All modules loaded")

    async def initialize(self):
        """Initialize all core systems"""
        if self.initialized:
            return

        try:
            # Setup event handlers
            self._setup_event_handlers()

            self.initialized = True
            logger.info("✅ Core System initialization complete")

        except Exception as e:
            logger.error(f"Core System initialization failed: {e}")
            raise

    def _setup_event_handlers(self):
        """Setup Discord event handlers"""

        @self.bot.event
        async def on_ready():
            await self.event_manager.on_ready()
            logger.info(f"🤖 {self.bot.user} is online and ready!")

        @self.bot.event
        async def on_message(message):
            await self.event_manager.on_message(message)

        @self.bot.event
        async def on_member_join(member):
            await self.event_manager.on_member_join(member)

        @self.bot.event
        async def on_raw_reaction_add(payload):
            await self.event_manager.on_raw_reaction_add(payload)

        @self.bot.event
        async def on_member_remove(member):
            await self.event_manager.on_member_remove(member)

        @self.bot.event
        async def on_guild_join(guild):
            await self.event_manager.on_guild_join(guild)

        @self.bot.event
        async def on_guild_remove(guild):
            await self.event_manager.on_guild_remove(guild)

    async def get_system_status(self) -> Dict:
        """Get comprehensive status of all core systems"""
        if not self.initialized:
            return {"status": "not_initialized"}

        return await self.event_manager.health_check()

    async def shutdown(self):
        """Graceful shutdown of all core systems"""
        logger.info("🔄 Initiating core system shutdown...")

        if self.initialized:
            await self.event_manager.broadcast_shutdown()

        self.initialized = False
        logger.info("✅ Core system shutdown complete")

    # Quick access methods for systems
    def get_ai_handler(self) -> AIHandler:
        return self.ai_handler

    def get_interactive_menus(self) -> InteractiveMenus:
        return self.interactive_menus

    def get_smart_moderation(self) -> SmartModerator:
        return self.smart_moderation

    def get_welcome_system(self) -> WelcomeSystem:
        return self.welcome_system

    def get_event_manager(self) -> EventManager:
        return self.event_manager


# Global core instance
_core_instance: Optional[CoreSystem] = None


def initialize_core(bot: commands.Bot) -> CoreSystem:
    """Initialize the core system singleton"""
    global _core_instance

    if _core_instance is None:
        _core_instance = CoreSystem(bot)

    return _core_instance


def get_core() -> Optional[CoreSystem]:
    """Get the initialized core system"""
    return _core_instance


async def startup_core(bot: commands.Bot) -> CoreSystem:
    """Complete core system startup"""
    core = initialize_core(bot)
    await core.initialize()
    return core
