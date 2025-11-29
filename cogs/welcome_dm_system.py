"""
🌟 Astra Welcome DM System
Sends personalized, dynamic welcome messages to users joining servers
Each message is uniquely generated with AI and personality adaptation

Created: November 3, 2025
Purpose: Build immediate personal connections with trust and warmth
"""

import asyncio
import logging
import sqlite3
import json
import time
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path

import discord
from discord.ext import commands, tasks
from discord import app_commands

logger = logging.getLogger("astra.welcome_dm_system")


class WelcomeDMSystem(commands.Cog):
    """
    🌟 Personalized Welcome DM System
    Sends dynamic, AI-generated welcome messages to new members
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = Path("data/welcome_dms.db")
        self.logger = logger

        # Statistics tracking
        self.stats = {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "dms_disabled": 0,
            "rate_limited": 0,
            "duplicate_prevented": 0,
        }

        # Rate limiting
        self.dm_queue: asyncio.Queue = asyncio.Queue()
        self.rate_limit_delay = 1.0  # 1 second between DMs
        self.processing_queue = False

        # Feature flags
        self.enabled = True
        self.bulk_operation_running = False

        # Initialize database
        self._init_database()

        # Import AI client
        try:
            from ai.universal_ai_client import UniversalAIClient

            self.ai_client = None  # Will be initialized when needed
            self.ai_available = True
            logger.info("✅ AI client available for welcome messages")
        except ImportError:
            self.ai_available = False
            logger.warning("⚠️ AI client not available - using fallback messages")

        # Import personality core
        try:
            from ai.bot_personality_core import BotPersonalityCore

            self.personality_core = None  # Will be initialized when needed
            self.personality_available = True
            logger.info("✅ Personality core available for adaptive messages")
        except ImportError:
            self.personality_available = False
            logger.warning("⚠️ Personality core not available - using standard tone")

        # Start queue processor
        self.dm_processor.start()

        logger.info("🌟 Welcome DM System initialized")

    def _init_database(self):
        """Initialize SQLite database for tracking sent DMs"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS welcome_dms (
                    user_id INTEGER PRIMARY KEY,
                    first_dm_sent_at TEXT,
                    servers_welcomed TEXT DEFAULT '[]',
                    total_servers INTEGER DEFAULT 0,
                    last_dm_timestamp TEXT,
                    opt_out INTEGER DEFAULT 0,
                    delivery_status TEXT,
                    message_preview TEXT,
                    metadata TEXT DEFAULT '{}'
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bulk_operation_log (
                    operation_id TEXT PRIMARY KEY,
                    started_at TEXT,
                    completed_at TEXT,
                    total_users INTEGER,
                    successful INTEGER,
                    failed INTEGER,
                    status TEXT,
                    metadata TEXT DEFAULT '{}'
                )
                """
            )

            conn.commit()

        logger.info("✅ Welcome DM database initialized")

    async def _get_ai_client(self):
        """Lazy load AI client"""
        if not self.ai_available:
            return None

        if self.ai_client is None:
            from ai.universal_ai_client import UniversalAIClient

            self.ai_client = UniversalAIClient(self.bot)

        return self.ai_client

    async def _get_personality_core(self):
        """Lazy load personality core"""
        if not self.personality_available:
            return None

        if self.personality_core is None:
            from ai.bot_personality_core import BotPersonalityCore

            self.personality_core = BotPersonalityCore(self.bot)

        return self.personality_core

    def _has_received_dm(self, user_id: int) -> bool:
        """Check if user has already received a welcome DM"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT user_id, opt_out FROM welcome_dms WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchone()

            if result:
                # Check if user opted out
                if result[1] == 1:
                    logger.info(f"User {user_id} has opted out of welcome DMs")
                    return True
                logger.info(f"User {user_id} already received welcome DM")
                self.stats["duplicate_prevented"] += 1
                return True

            return False

    def _log_dm_sent(
        self,
        user_id: int,
        guild_id: int,
        success: bool,
        status: str,
        message_preview: str = "",
    ):
        """Log DM delivery to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT servers_welcomed, total_servers FROM welcome_dms WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchone()

            if result:
                # Update existing record
                servers = json.loads(result[0])
                servers.append(guild_id)
                total = result[1] + 1

                conn.execute(
                    """
                    UPDATE welcome_dms
                    SET servers_welcomed = ?,
                        total_servers = ?,
                        last_dm_timestamp = ?,
                        delivery_status = ?,
                        message_preview = ?
                    WHERE user_id = ?
                    """,
                    (
                        json.dumps(servers),
                        total,
                        datetime.now(timezone.utc).isoformat(),
                        status,
                        message_preview[:200],
                        user_id,
                    ),
                )
            else:
                # Insert new record
                conn.execute(
                    """
                    INSERT INTO welcome_dms (
                        user_id,
                        first_dm_sent_at,
                        servers_welcomed,
                        total_servers,
                        last_dm_timestamp,
                        delivery_status,
                        message_preview
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        datetime.now(timezone.utc).isoformat(),
                        json.dumps([guild_id]),
                        1,
                        datetime.now(timezone.utc).isoformat(),
                        status,
                        message_preview[:200],
                    ),
                )

            conn.commit()

        # Update statistics
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1

    async def generate_welcome_message(
        self, user: discord.User, guild: discord.Guild, context: Dict[str, Any]
    ) -> str:
        """
        Generate dynamic, personalized welcome message using AI

        Args:
            user: Discord user who joined
            guild: Guild they joined
            context: Additional context (account_age, is_returning, etc.)

        Returns:
            Personalized welcome message string
        """
        # Try to get AI client
        ai_client = await self._get_ai_client()
        personality_core = await self._get_personality_core()

        # Build comprehensive context for AI
        account_age_days = context.get("account_age_days", 0)
        is_new_to_discord = account_age_days < 30
        is_returning = context.get("is_returning", False)
        guild_size = guild.member_count if guild else 0
        hour = datetime.now(timezone.utc).hour

        # Determine greeting based on time
        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 22:
            time_greeting = "Good evening"
        else:
            time_greeting = "Hey"

        # If AI is available, generate dynamic message
        if ai_client and self.ai_available:
            try:
                # Build AI prompt for welcome message generation
                prompt = f"""Generate a warm, personal welcome DM for a Discord user who just joined a server.

USER CONTEXT:
- Username: {user.display_name}
- Server they joined: {guild.name if guild else 'a server'}
- Server size: {guild_size} members
- Account age: {account_age_days} days old
- New to Discord: {is_new_to_discord}
- Has seen Astra before: {is_returning}
- Time of day: {time_greeting}

YOUR IDENTITY:
You are Astra, an advanced AI companion bot with:
- 🛡️ Intelligent moderation & security systems
- ⚖️ Fair appeals process for violations
- 🤖 Adaptive personality that connects with each person uniquely
- 🌌 Community features (space facts, quizzes, analytics, events)
- 📊 Comprehensive server management tools
- 💫 Trusted friend and companion, not just a bot

REQUIREMENTS:
1. Start with warm, personal greeting (use time context naturally)
2. Introduce yourself as Astra - emphasize being a FRIEND and COMPANION
3. Briefly mention 2-3 most relevant capabilities (naturally, not list format)
4. Build TRUST - emphasize you're reliable, helpful, always available
5. Position yourself as someone they can talk to, ask questions, rely on
6. End with warm invitation to add you to their favorite servers
7. Mention you "supercharge communities" and handle "literally everything"
8. Keep tone: friendly, warm, personal, trustworthy (NOT corporate or formal)
9. Length: 150-200 words (conversational, not too long)
10. NO markdown formatting or emojis overload - natural and warm

ADAPT TO USER:
- If new to Discord: Be more welcoming, explain basics
- If experienced: Be more direct, highlight advanced features
- If returning user: Acknowledge previous connection warmly
- If large server: Emphasize community management
- If small server: Emphasize personal touch

Generate ONLY the message text, no explanations or notes."""

                # Generate with AI
                response = await ai_client.generate_response(
                    prompt=prompt,
                    user_id=user.id,
                    guild_id=guild.id if guild else None,
                    max_tokens=400,
                    temperature=0.9,  # Higher creativity for unique messages
                )

                if response and len(response.strip()) > 50:
                    logger.info(f"✅ Generated AI welcome message for {user.name}")
                    return response.strip()
                else:
                    logger.warning("AI response too short, using fallback")

            except Exception as e:
                logger.error(f"Error generating AI welcome message: {e}")

        # Fallback to dynamic template-based generation
        return self._generate_fallback_message(
            user, guild, context, time_greeting, is_new_to_discord, is_returning
        )

    def _generate_fallback_message(
        self,
        user: discord.User,
        guild: discord.Guild,
        context: Dict[str, Any],
        time_greeting: str,
        is_new_to_discord: bool,
        is_returning: bool,
    ) -> str:
        """Generate fallback message when AI is unavailable"""

        guild_name = guild.name if guild else "a new server"
        user_name = user.display_name

        if is_returning:
            message = f"{time_greeting}, {user_name}! 🎊\n\n"
            message += f"Great to see you in another server! It's Astra - we've crossed paths before, and I'm excited to be your companion in {guild_name} too!\n\n"
            message += "Different server, same trustworthy AI friend who's here for whatever you need - from keeping the community safe to just having a chat at 2 AM. I remember our previous interactions, so we can pick up right where we left off!\n\n"
            message += "I bring intelligent moderation, comprehensive security, and that personal touch to every community I'm part of. Think of me as both a powerful management system and a genuine friend.\n\n"
            message += "If you're enjoying having me around in multiple servers, why not add me to all your favorites? I can supercharge any community with AI-powered management and make them more inclusive, safer, and genuinely better places to be.\n\n"
            message += "Thanks for being part of my extended community! Let's make this space amazing too! 💙"

        elif is_new_to_discord:
            message = f"{time_greeting}! 👋 Welcome to {guild_name}!\n\n"
            message += f"I'm Astra - think of me as your friendly AI companion who's here to make your Discord experience amazing! I noticed your account is pretty new, so let me be the first to say: you're in for a great time here!\n\n"
            message += "I help keep this community safe and welcoming with smart moderation (don't worry, I'm fair!), and I'm always around if you want to chat, have questions, or need help with anything. Seriously, anything - from space facts to server management, I've got you covered!\n\n"
            message += "Consider me a friend you can trust. I adapt to each person uniquely, so our conversations will always feel natural and personal. 💫\n\n"
            message += "Oh, and if you love what you see here - you should totally add me to your other favorite servers! I can supercharge any community with AI-powered management, security, moderation, events, and literally everything else. I'm basically a Swiss Army knife, but friendlier. 😊\n\n"
            message += "Welcome aboard! Let's make some awesome memories together! 🚀"

        else:
            message = f"Welcome to {guild_name}, {user_name}! 🎉\n\n"
            message += "I'm Astra - the AI powering this community. You've probably seen bots before, but I like to think I'm a bit different. I combine intelligent moderation with actual personality, so you're talking to a companion, not just a command processor.\n\n"
            message += "I handle everything from security and appeals to analytics and community engagement - all with adaptive responses tailored to each person. Whether you need help navigating the server, want to discuss quantum physics, or just need someone to chat with, I'm here.\n\n"
            message += "Think of me as both a powerful management system and a trusted friend. I learn, adapt, and actually care about making this place better for everyone. ✨\n\n"
            message += "Love having an AI companion who actually gets it? Share the experience! Add me to your favorite servers and watch me supercharge them with intelligent moderation, comprehensive security, community tools, and that personal touch that makes all the difference.\n\n"
            message += "Looking forward to getting to know you! 🌟"

        return message

    async def send_welcome_dm(
        self, user: discord.User, guild: discord.Guild
    ) -> Dict[str, Any]:
        """
        Send welcome DM to a user

        Returns:
            Dictionary with status and details
        """
        # Check if already sent
        if self._has_received_dm(user.id):
            return {
                "success": False,
                "status": "duplicate",
                "message": "User already received welcome DM",
            }

        # Check if user is a bot
        if user.bot:
            return {
                "success": False,
                "status": "bot_user",
                "message": "User is a bot",
            }

        # Gather context about user
        account_age = (datetime.now(timezone.utc) - user.created_at).days

        # Check if user has been welcomed before
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT total_servers FROM welcome_dms WHERE user_id = ?", (user.id,)
            )
            result = cursor.fetchone()
            is_returning = result is not None and result[0] > 0

        context = {
            "account_age_days": account_age,
            "is_returning": is_returning,
            "guild_size": guild.member_count if guild else 0,
        }

        try:
            # Generate personalized message
            message_content = await self.generate_welcome_message(user, guild, context)

            # Create embed for visual appeal
            embed = discord.Embed(
                title="✨ Welcome from Astra!",
                description=message_content,
                color=0x00FFD4,
                timestamp=datetime.now(timezone.utc),
            )

            # Add server context
            if guild:
                embed.set_footer(
                    text=f"You joined: {guild.name}",
                    icon_url=guild.icon.url if guild.icon else None,
                )

            # Add Astra's avatar
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            # Send DM
            await user.send(embed=embed)

            # Log success
            self._log_dm_sent(
                user.id, guild.id, True, "delivered", message_content[:200]
            )

            logger.info(f"✅ Welcome DM sent to {user.name} ({user.id})")

            return {
                "success": True,
                "status": "delivered",
                "message": "Welcome DM sent successfully",
                "preview": message_content[:100],
            }

        except discord.Forbidden:
            # User has DMs disabled
            self._log_dm_sent(user.id, guild.id, False, "dms_disabled")
            self.stats["dms_disabled"] += 1
            logger.warning(f"⚠️ Cannot send DM to {user.name} - DMs disabled")

            return {
                "success": False,
                "status": "dms_disabled",
                "message": "User has DMs disabled",
            }

        except discord.HTTPException as e:
            # Other Discord API error
            self._log_dm_sent(user.id, guild.id, False, f"error: {str(e)}")
            logger.error(f"❌ Discord API error sending DM to {user.name}: {e}")

            return {
                "success": False,
                "status": "api_error",
                "message": f"Discord API error: {str(e)}",
            }

        except Exception as e:
            # Unexpected error
            self._log_dm_sent(user.id, guild.id, False, f"error: {str(e)}")
            logger.error(f"❌ Unexpected error sending welcome DM to {user.name}: {e}")

            return {
                "success": False,
                "status": "error",
                "message": f"Error: {str(e)}",
            }

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Automatic welcome DM when user joins any server
        Triggered by Discord's on_member_join event
        """
        if not self.enabled:
            return

        # Don't DM bots
        if member.bot:
            return

        # Add delay for natural feel (3-5 seconds)
        await asyncio.sleep(3.5)

        # Add to queue for rate-limited processing
        await self.dm_queue.put((member, member.guild))

        logger.info(
            f"👋 New member {member.name} joined {member.guild.name} - queued for welcome DM"
        )

    @tasks.loop(seconds=1.2)
    async def dm_processor(self):
        """
        Process DM queue with rate limiting
        Sends 1 DM every 1.2 seconds to avoid Discord API limits
        """
        if self.dm_queue.empty():
            return

        try:
            # Get next user from queue
            user, guild = await asyncio.wait_for(self.dm_queue.get(), timeout=0.1)

            # Send welcome DM
            result = await self.send_welcome_dm(user, guild)

            self.stats["total_sent"] += 1

            # Log result
            if result["success"]:
                logger.info(
                    f"✅ Processed welcome DM for {user.name} - {result['status']}"
                )
            else:
                logger.warning(
                    f"⚠️ Failed to send DM to {user.name} - {result['status']}"
                )

        except asyncio.TimeoutError:
            # Queue was empty
            pass
        except Exception as e:
            logger.error(f"Error processing DM queue: {e}")

    @dm_processor.before_loop
    async def before_dm_processor(self):
        """Wait until bot is ready before processing queue"""
        await self.bot.wait_until_ready()

    # ============================================================================
    # ADMIN COMMANDS
    # ============================================================================

    @app_commands.command(name="welcome_dm_test")
    @app_commands.describe(user="User to send test welcome DM to")
    async def test_welcome_dm(
        self, interaction: discord.Interaction, user: discord.User
    ):
        """🧪 Send a test welcome DM to a specific user"""
        # Check if user is bot owner
        logger.info(
            f"🔍 Owner check - Your ID: {interaction.user.id}, Bot owner_id: {self.bot.owner_id}"
        )
        if self.bot.owner_id is None:
            await interaction.response.send_message(
                "⚠️ Bot owner ID not configured! Please set OWNER_ID in .env file.",
                ephemeral=True,
            )
            return
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can use this command.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # Send test DM
        result = await self.send_welcome_dm(user, interaction.guild)

        if result["success"]:
            await interaction.followup.send(
                f"✅ Test welcome DM sent to {user.mention}!\n\n**Preview:**\n{result.get('preview', 'N/A')}...",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"❌ Failed to send test DM: {result['status']}\n{result['message']}",
                ephemeral=True,
            )

    @app_commands.command(name="welcome_dm_stats")
    async def welcome_dm_stats(self, interaction: discord.Interaction):
        """📊 View welcome DM statistics"""
        # Check if user is bot owner or admin
        if not (
            interaction.user.id == self.bot.owner_id
            or interaction.user.guild_permissions.administrator
        ):
            await interaction.response.send_message(
                "❌ Only administrators can view these statistics.", ephemeral=True
            )
            return

        # Get database stats
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM welcome_dms")
            total_users = cursor.fetchone()[0]

            cursor = conn.execute(
                "SELECT COUNT(*) FROM welcome_dms WHERE delivery_status = 'delivered'"
            )
            successful = cursor.fetchone()[0]

            cursor = conn.execute(
                "SELECT COUNT(*) FROM welcome_dms WHERE delivery_status = 'dms_disabled'"
            )
            dms_disabled = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM welcome_dms WHERE opt_out = 1")
            opted_out = cursor.fetchone()[0]

        # Calculate success rate
        success_rate = (successful / total_users * 100) if total_users > 0 else 0

        embed = discord.Embed(
            title="📊 Welcome DM System Statistics",
            description="Comprehensive delivery and engagement metrics",
            color=0x00FFD4,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📨 Total DMs Attempted",
            value=f"**{self.stats['total_sent']:,}**",
            inline=True,
        )

        embed.add_field(
            name="✅ Successful Deliveries",
            value=f"**{self.stats['successful']:,}**",
            inline=True,
        )

        embed.add_field(
            name="📈 Success Rate", value=f"**{success_rate:.1f}%**", inline=True
        )

        embed.add_field(
            name="👥 Unique Users Reached", value=f"**{total_users:,}**", inline=True
        )

        embed.add_field(
            name="🚫 DMs Disabled",
            value=f"**{self.stats['dms_disabled']:,}**",
            inline=True,
        )

        embed.add_field(
            name="🔄 Duplicates Prevented",
            value=f"**{self.stats['duplicate_prevented']:,}**",
            inline=True,
        )

        embed.add_field(
            name="❌ Failed Deliveries",
            value=f"**{self.stats['failed']:,}**",
            inline=True,
        )

        embed.add_field(name="⛔ Opted Out", value=f"**{opted_out:,}**", inline=True)

        embed.add_field(
            name="⏱️ Rate Limited",
            value=f"**{self.stats['rate_limited']:,}**",
            inline=True,
        )

        embed.add_field(
            name="🔄 Queue Status",
            value=f"**{self.dm_queue.qsize()}** pending",
            inline=True,
        )

        embed.add_field(
            name="⚙️ System Status",
            value=f"**{'Enabled' if self.enabled else 'Disabled'}**",
            inline=True,
        )

        embed.add_field(
            name="🤖 AI Generation",
            value=f"**{'Active' if self.ai_available else 'Fallback'}**",
            inline=True,
        )

        embed.set_footer(text="Astra Welcome DM System")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="welcome_dm_toggle")
    @app_commands.describe(enabled="Enable or disable automatic welcome DMs")
    async def toggle_welcome_dms(self, interaction: discord.Interaction, enabled: bool):
        """⚙️ Enable or disable automatic welcome DMs"""
        # Check if user is bot owner
        logger.info(
            f"🔍 Toggle - Your ID: {interaction.user.id}, Bot owner_id: {self.bot.owner_id}"
        )
        if self.bot.owner_id is None:
            await interaction.response.send_message(
                "⚠️ Bot owner ID not configured! Please set OWNER_ID in .env file.",
                ephemeral=True,
            )
            return
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can toggle this system.", ephemeral=True
            )
            return

        self.enabled = enabled

        status = "✅ enabled" if enabled else "❌ disabled"
        await interaction.response.send_message(
            f"Welcome DM system is now {status}.", ephemeral=True
        )

        logger.info(f"Welcome DM system {'enabled' if enabled else 'disabled'}")

    # ============================================================================
    # BULK DM OPERATION
    # ============================================================================

    @app_commands.command(name="welcome_dm_bulk")
    @app_commands.describe(
        mode="Choose operation mode: preview, test_sample, or full_send",
        sample_size="For test_sample mode: number of users to test (default: 10)",
    )
    async def bulk_welcome_dms(
        self,
        interaction: discord.Interaction,
        mode: str = "preview",
        sample_size: int = 10,
    ):
        """
        📤 Send welcome DMs to all existing members across all servers

        Modes:
        - preview: See statistics without sending
        - test_sample: Send to a small sample for testing
        - full_send: Send to all eligible users (requires confirmation)
        """
        # Check if user is bot owner
        logger.info(
            f"🔍 Bulk DM - Your ID: {interaction.user.id}, Bot owner_id: {self.bot.owner_id}"
        )
        if self.bot.owner_id is None:
            await interaction.response.send_message(
                "⚠️ Bot owner ID not configured! Please set OWNER_ID in .env file.",
                ephemeral=True,
            )
            return
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can run bulk operations.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # Check if bulk operation is already running
        if self.bulk_operation_running:
            await interaction.followup.send(
                "⚠️ A bulk operation is already in progress. Please wait for it to complete.",
                ephemeral=True,
            )
            return

        # Gather all users across all guilds
        all_users = set()
        guild_stats = []

        for guild in self.bot.guilds:
            guild_members = [m for m in guild.members if not m.bot]
            all_users.update([m.id for m in guild_members])
            guild_stats.append(
                {
                    "name": guild.name,
                    "total_members": guild.member_count,
                    "non_bot_members": len(guild_members),
                }
            )

        # Filter out users who already received DMs
        eligible_users = []
        with sqlite3.connect(self.db_path) as conn:
            for user_id in all_users:
                cursor = conn.execute(
                    "SELECT user_id, opt_out FROM welcome_dms WHERE user_id = ?",
                    (user_id,),
                )
                result = cursor.fetchone()

                # User is eligible if they haven't received a DM and haven't opted out
                if not result or result[1] == 0:
                    user = self.bot.get_user(user_id)
                    if user:
                        eligible_users.append(user)

        # Create statistics embed
        stats_embed = discord.Embed(
            title="📊 Bulk Welcome DM Operation - Statistics",
            description=f"**Mode:** `{mode}`",
            color=0x00FFD4,
            timestamp=datetime.now(timezone.utc),
        )

        stats_embed.add_field(
            name="🏰 Total Servers", value=f"**{len(self.bot.guilds)}**", inline=True
        )

        stats_embed.add_field(
            name="👥 Total Unique Users", value=f"**{len(all_users):,}**", inline=True
        )

        stats_embed.add_field(
            name="✅ Eligible for DM", value=f"**{len(eligible_users):,}**", inline=True
        )

        stats_embed.add_field(
            name="⏭️ Already Received",
            value=f"**{len(all_users) - len(eligible_users):,}**",
            inline=True,
        )

        # Add guild breakdown (top 10)
        guild_breakdown = "\n".join(
            [
                f"• **{g['name']}**: {g['non_bot_members']} members"
                for g in sorted(
                    guild_stats, key=lambda x: x["non_bot_members"], reverse=True
                )[:10]
            ]
        )

        if len(guild_stats) > 10:
            guild_breakdown += f"\n• *...and {len(guild_stats) - 10} more servers*"

        stats_embed.add_field(
            name="📋 Server Breakdown (Top 10)", value=guild_breakdown, inline=False
        )

        # PREVIEW MODE
        if mode == "preview":
            estimated_time = len(eligible_users) * 1.2  # seconds
            hours = int(estimated_time // 3600)
            minutes = int((estimated_time % 3600) // 60)

            stats_embed.add_field(
                name="⏱️ Estimated Time",
                value=f"**{hours}h {minutes}m** at 1 DM per 1.2 seconds",
                inline=False,
            )

            stats_embed.set_footer(
                text="Run with mode='test_sample' to test on a small sample first"
            )

            await interaction.followup.send(embed=stats_embed, ephemeral=True)
            return

        # TEST SAMPLE MODE
        elif mode == "test_sample":
            sample_size = min(sample_size, len(eligible_users))
            test_users = eligible_users[:sample_size]

            confirm_embed = discord.Embed(
                title="🧪 Test Sample Mode",
                description=f"Ready to send welcome DMs to **{sample_size}** users for testing.",
                color=0xFFAA00,
            )

            confirm_embed.add_field(
                name="⚠️ Confirmation Required",
                value=f"React with ✅ to proceed or ❌ to cancel.",
                inline=False,
            )

            await interaction.followup.send(embed=confirm_embed, ephemeral=True)

            # Start test sample operation
            asyncio.create_task(
                self._run_bulk_operation(
                    interaction.user,
                    test_users,
                    f"test_sample_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                    is_test=True,
                )
            )

        # FULL SEND MODE
        elif mode == "full_send":
            if len(eligible_users) == 0:
                await interaction.followup.send(
                    "✅ All users have already received welcome DMs!", ephemeral=True
                )
                return

            confirm_embed = discord.Embed(
                title="🚨 FULL BULK OPERATION - CONFIRMATION REQUIRED",
                description=f"You are about to send welcome DMs to **{len(eligible_users):,}** users across **{len(self.bot.guilds)}** servers.",
                color=0xFF0000,
            )

            estimated_time = len(eligible_users) * 1.2
            hours = int(estimated_time // 3600)
            minutes = int((estimated_time % 3600) // 60)

            confirm_embed.add_field(
                name="⏱️ Estimated Duration",
                value=f"**{hours}h {minutes}m**",
                inline=True,
            )

            confirm_embed.add_field(
                name="⚡ Rate", value="**1 DM per 1.2s**", inline=True
            )

            confirm_embed.add_field(
                name="⚠️ IMPORTANT",
                value="• This operation cannot be easily stopped once started\n• Users with DMs disabled will be skipped\n• Progress will be logged in real-time\n• You'll receive updates every 100 DMs",
                inline=False,
            )

            confirm_embed.add_field(
                name="✅ To Proceed",
                value="Type exactly: `CONFIRM BULK SEND` in your next message within 60 seconds",
                inline=False,
            )

            confirm_embed.set_footer(
                text="⚠️ This is a one-time operation for all existing members"
            )

            await interaction.followup.send(embed=confirm_embed, ephemeral=True)

            # Wait for confirmation
            def check(m):
                return (
                    m.author.id == interaction.user.id
                    and m.channel.id == interaction.channel.id
                    and m.content == "CONFIRM BULK SEND"
                )

            try:
                await self.bot.wait_for("message", check=check, timeout=60.0)

                # Confirmation received - start bulk operation
                await interaction.channel.send(
                    f"✅ {interaction.user.mention} Bulk operation confirmed! Starting...",
                    delete_after=10,
                )

                asyncio.create_task(
                    self._run_bulk_operation(
                        interaction.user,
                        eligible_users,
                        f"bulk_full_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                        is_test=False,
                    )
                )

            except asyncio.TimeoutError:
                await interaction.channel.send(
                    f"⏱️ {interaction.user.mention} Bulk operation timed out - no confirmation received.",
                    delete_after=10,
                )

        else:
            await interaction.followup.send(
                f"❌ Invalid mode: `{mode}`. Use: preview, test_sample, or full_send",
                ephemeral=True,
            )

    async def _run_bulk_operation(
        self,
        initiator: discord.User,
        users: List[discord.User],
        operation_id: str,
        is_test: bool = False,
    ):
        """
        Execute bulk DM operation with progress tracking

        Args:
            initiator: User who started the operation
            users: List of users to send DMs to
            operation_id: Unique identifier for this operation
            is_test: Whether this is a test operation
        """
        self.bulk_operation_running = True
        start_time = time.time()

        # Log operation start
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO bulk_operation_log (
                    operation_id, started_at, total_users, status
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    operation_id,
                    datetime.now(timezone.utc).isoformat(),
                    len(users),
                    "running",
                ),
            )
            conn.commit()

        logger.info(f"🚀 Starting bulk operation {operation_id} - {len(users)} users")

        # Send initial progress message to initiator
        try:
            progress_embed = discord.Embed(
                title="📤 Bulk Welcome DM Operation Started",
                description=f"**Operation ID:** `{operation_id}`\n**Target Users:** {len(users):,}\n**Mode:** {'Test Sample' if is_test else 'Full Send'}",
                color=0x00FFD4,
                timestamp=datetime.now(timezone.utc),
            )
            await initiator.send(embed=progress_embed)
        except:
            pass

        # Process users
        successful = 0
        failed = 0
        dms_disabled = 0

        for idx, user in enumerate(users, 1):
            try:
                # Get random guild where this user is a member for context
                user_guild = None
                for guild in self.bot.guilds:
                    if guild.get_member(user.id):
                        user_guild = guild
                        break

                # Send DM
                result = await self.send_welcome_dm(user, user_guild)

                if result["success"]:
                    successful += 1
                elif result["status"] == "dms_disabled":
                    dms_disabled += 1
                    failed += 1
                else:
                    failed += 1

                # Send progress update every 100 users
                if idx % 100 == 0:
                    progress = (idx / len(users)) * 100
                    elapsed = time.time() - start_time
                    avg_time_per_dm = elapsed / idx
                    remaining = (len(users) - idx) * avg_time_per_dm

                    try:
                        progress_msg = (
                            f"📊 **Progress Update**\n"
                            f"Processed: {idx:,}/{len(users):,} ({progress:.1f}%)\n"
                            f"✅ Successful: {successful:,}\n"
                            f"❌ Failed: {failed:,}\n"
                            f"🚫 DMs Disabled: {dms_disabled:,}\n"
                            f"⏱️ Remaining: ~{int(remaining/60)} minutes"
                        )
                        await initiator.send(progress_msg)
                    except:
                        pass

                # Rate limiting
                await asyncio.sleep(1.2)

            except Exception as e:
                logger.error(f"Error in bulk operation for user {user.id}: {e}")
                failed += 1

        # Operation complete
        end_time = time.time()
        duration = end_time - start_time

        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE bulk_operation_log
                SET completed_at = ?,
                    successful = ?,
                    failed = ?,
                    status = ?
                WHERE operation_id = ?
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    successful,
                    failed,
                    "completed",
                    operation_id,
                ),
            )
            conn.commit()

        # Send completion message
        try:
            completion_embed = discord.Embed(
                title="✅ Bulk Welcome DM Operation Complete!",
                description=f"**Operation ID:** `{operation_id}`",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            completion_embed.add_field(
                name="📊 Results",
                value=(
                    f"**Total Processed:** {len(users):,}\n"
                    f"**✅ Successful:** {successful:,}\n"
                    f"**❌ Failed:** {failed:,}\n"
                    f"**🚫 DMs Disabled:** {dms_disabled:,}"
                ),
                inline=False,
            )

            success_rate = (successful / len(users) * 100) if len(users) > 0 else 0
            completion_embed.add_field(
                name="📈 Success Rate", value=f"**{success_rate:.1f}%**", inline=True
            )

            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)

            completion_embed.add_field(
                name="⏱️ Duration",
                value=f"**{hours}h {minutes}m {seconds}s**",
                inline=True,
            )

            completion_embed.set_footer(text="Bulk operation completed successfully")

            await initiator.send(embed=completion_embed)

        except Exception as e:
            logger.error(f"Could not send completion message: {e}")

        self.bulk_operation_running = False
        logger.info(
            f"✅ Bulk operation {operation_id} completed - {successful}/{len(users)} successful"
        )

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.dm_processor.cancel()
        logger.info("🌟 Welcome DM System unloaded")


async def setup(bot: commands.Bot):
    """Load the WelcomeDMSystem cog"""
    await bot.add_cog(WelcomeDMSystem(bot))
    logger.info("✅ WelcomeDMSystem cog loaded")
