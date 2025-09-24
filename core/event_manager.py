"""
Event Manager - Central event coordination and bot lifecycle management
Coordinates all core systems and handles Discord events - Maximum 200 lines
"""

import asyncio
import logging
from typing import Dict, List, Optional
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.events")


class EventManager:
    """Central event coordinator for all core systems"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.systems = {}  # system_name -> system_instance
        self.event_stats = {
            "messages_processed": 0,
            "members_welcomed": 0,
            "moderation_actions": 0,
            "ai_interactions": 0,
            "menu_interactions": 0,
        }

        # System readiness tracking
        self.systems_ready = {
            "ai_handler": False,
            "interactive_menus": False,
            "smart_moderation": False,
            "welcome_system": False,
        }

    def register_system(self, name: str, system_instance):
        """Register a core system with the event manager"""
        self.systems[name] = system_instance
        self.systems_ready[name] = True
        logger.info(f"Registered system: {name}")

    async def on_ready(self):
        """Handle bot ready event"""
        logger.info(
            f"🚀 Event Manager initialized - {len(self.systems)} systems registered"
        )

        # Verify all critical systems are ready
        missing_systems = [
            name for name, ready in self.systems_ready.items() if not ready
        ]
        if missing_systems:
            logger.warning(f"Missing systems: {missing_systems}")
        else:
            logger.info("✅ All core systems ready")

    async def on_message(self, message: discord.Message):
        """Coordinate message processing across all systems"""
        if message.author.bot:
            return

        self.event_stats["messages_processed"] += 1

        # 1. Check moderation first (highest priority)
        if "smart_moderation" in self.systems:
            moderation_action = await self.systems["smart_moderation"].check_message(
                message
            )
            if moderation_action:
                self.event_stats["moderation_actions"] += 1
                return  # Stop processing if moderated

        # 2. Check for AI interaction
        if "ai_handler" in self.systems:
            if self.bot.user.mentioned_in(
                message
            ) or message.content.lower().startswith(("astra", "hey astra", "hi astra")):
                await self.systems["ai_handler"].process_message(message)
                self.event_stats["ai_interactions"] += 1
                return

    async def on_member_join(self, member: discord.Member):
        """Handle new member joining"""
        self.event_stats["members_welcomed"] += 1

        if "welcome_system" in self.systems:
            await self.systems["welcome_system"].handle_new_member(member)

        logger.info(f"New member joined: {member} in {member.guild}")

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle emoji reactions on interactive menus"""
        if payload.user_id == self.bot.user.id:
            return

        if "interactive_menus" in self.systems:
            handled = await self.systems["interactive_menus"].handle_reaction(payload)
            if handled:
                self.event_stats["menu_interactions"] += 1

    async def on_member_remove(self, member: discord.Member):
        """Handle member leaving"""
        logger.info(f"Member left: {member} from {member.guild}")

        # Clean up any user-specific data
        for system in self.systems.values():
            if hasattr(system, "cleanup_user_data"):
                try:
                    await system.cleanup_user_data(member.id)
                except Exception as e:
                    logger.error(f"Error cleaning up user data: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        """Handle bot joining new guild"""
        logger.info(
            f"🏰 Joined new guild: {guild.name} ({guild.id}) - {guild.member_count} members"
        )

        # Initialize welcome system for new guild
        if "welcome_system" in self.systems:
            # Set default configuration
            self.systems["welcome_system"].update_guild_config(
                guild.id,
                {"enabled": True, "channel_name": "welcome", "dm_welcome": False},
            )

    async def on_guild_remove(self, guild: discord.Guild):
        """Handle bot leaving guild"""
        logger.info(f"Left guild: {guild.name} ({guild.id})")

        # Clean up guild-specific data
        for system in self.systems.values():
            if hasattr(system, "cleanup_guild_data"):
                try:
                    await system.cleanup_guild_data(guild.id)
                except Exception as e:
                    logger.error(f"Error cleaning up guild data: {e}")

    async def on_error(self, event_name: str, *args, **kwargs):
        """Handle event errors"""
        logger.error(f"Error in event {event_name}", exc_info=True)

    async def health_check(self) -> Dict:
        """Perform health check on all systems"""
        health_status = {
            "event_manager": "healthy",
            "systems": {},
            "stats": self.event_stats.copy(),
        }

        # Check each system
        for name, system in self.systems.items():
            try:
                if hasattr(system, "get_stats"):
                    system_stats = system.get_stats()
                    health_status["systems"][name] = {
                        "status": "healthy",
                        "stats": system_stats,
                    }
                else:
                    health_status["systems"][name] = {"status": "healthy"}
            except Exception as e:
                health_status["systems"][name] = {"status": "error", "error": str(e)}
                logger.error(f"Health check failed for {name}: {e}")

        return health_status

    async def broadcast_shutdown(self):
        """Notify all systems of impending shutdown"""
        logger.info("🔄 Broadcasting shutdown signal to all systems...")

        for name, system in self.systems.items():
            try:
                if hasattr(system, "shutdown"):
                    await system.shutdown()
                    logger.info(f"✅ {name} shutdown complete")
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    def get_system(self, name: str):
        """Get a registered system by name"""
        return self.systems.get(name)

    def get_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        stats = {
            "event_stats": self.event_stats.copy(),
            "systems_registered": len(self.systems),
            "systems_ready": sum(1 for ready in self.systems_ready.values() if ready),
            "uptime_events": self.event_stats["messages_processed"]
            + self.event_stats["members_welcomed"],
        }

        # Add individual system stats
        for name, system in self.systems.items():
            try:
                if hasattr(system, "get_stats"):
                    stats[f"{name}_stats"] = system.get_stats()
            except:
                pass

        return stats

    async def emergency_stop(self):
        """Emergency stop all systems"""
        logger.critical("🚨 EMERGENCY STOP initiated")

        # Disable all systems
        for name in self.systems_ready:
            self.systems_ready[name] = False

        # Broadcast emergency shutdown
        await self.broadcast_shutdown()

        logger.critical("🛑 All systems stopped")
