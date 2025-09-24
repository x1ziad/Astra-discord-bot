"""
Smart Moderation System - Automated monitoring and progressive warnings
Handles spam detection, toxic behavior, and member protection - Maximum 250 lines
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.moderation")


class SmartModerator:
    """Intelligent moderation system with progressive warnings"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_warnings = defaultdict(list)  # user_id -> [warning_timestamps]
        self.message_history = defaultdict(deque)  # user_id -> recent messages
        self.spam_tracking = defaultdict(int)  # user_id -> spam_count
        self.muted_users = set()  # Currently muted user IDs

        # Configuration
        self.config = {
            "spam_threshold": 5,  # Messages in timeframe
            "spam_timeframe": 10,  # Seconds
            "warning_decay": 3600,  # 1 hour warning decay
            "mute_duration": 300,  # 5 minutes initial mute
            "max_warnings": 3,
            "message_similarity_threshold": 0.8,
            "caps_threshold": 0.7,
            "mention_spam_limit": 5,
        }

    async def check_message(self, message: discord.Message) -> bool:
        """Check message for moderation issues - returns True if action taken"""
        if not message.guild or message.author.bot:
            return False

        user_id = message.author.id
        content = message.content.lower().strip()

        # Track message history
        self.message_history[user_id].append(
            {"content": content, "timestamp": time.time(), "message": message}
        )

        # Keep only recent messages (last 30 seconds)
        current_time = time.time()
        while (
            self.message_history[user_id]
            and current_time - self.message_history[user_id][0]["timestamp"] > 30
        ):
            self.message_history[user_id].popleft()

        # Run moderation checks
        violation_type = await self._detect_violations(message, user_id, content)

        if violation_type:
            await self._handle_violation(message, violation_type)
            return True

        return False

    async def _detect_violations(
        self, message: discord.Message, user_id: int, content: str
    ) -> Optional[str]:
        """Detect various types of violations"""

        # 1. Spam Detection
        if await self._is_spam(user_id, content):
            return "spam"

        # 2. Excessive Caps
        if await self._is_excessive_caps(content):
            return "caps_spam"

        # 3. Mention Spam
        if await self._is_mention_spam(message):
            return "mention_spam"

        # 4. Repeated Messages
        if await self._is_repeated_message(user_id, content):
            return "repeated_content"

        return None

    async def _is_spam(self, user_id: int, content: str) -> bool:
        """Check for spam based on message frequency"""
        recent_messages = [
            msg
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= self.config["spam_timeframe"]
        ]

        return len(recent_messages) >= self.config["spam_threshold"]

    async def _is_excessive_caps(self, content: str) -> bool:
        """Check for excessive capital letters"""
        if len(content) < 10:  # Too short to judge
            return False

        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        return caps_ratio >= self.config["caps_threshold"]

    async def _is_mention_spam(self, message: discord.Message) -> bool:
        """Check for mention spam"""
        return len(message.mentions) >= self.config["mention_spam_limit"]

    async def _is_repeated_message(self, user_id: int, content: str) -> bool:
        """Check for repeated identical or similar messages"""
        if len(content) < 5:  # Too short to be spam
            return False

        recent_contents = [
            msg["content"]
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= 60  # Last minute
        ]

        # Count identical messages
        identical_count = sum(
            1 for msg_content in recent_contents if msg_content == content
        )
        if identical_count >= 3:
            return True

        # Check for similar messages (simple similarity)
        similar_count = 0
        for msg_content in recent_contents:
            if msg_content != content and len(msg_content) > 10:
                similarity = self._calculate_similarity(content, msg_content)
                if similarity >= self.config["message_similarity_threshold"]:
                    similar_count += 1

        return similar_count >= 2

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    async def _handle_violation(self, message: discord.Message, violation_type: str):
        """Handle detected violation with progressive punishment"""
        user = message.author
        user_id = user.id

        # Clean up old warnings
        self._cleanup_old_warnings(user_id)

        # Add new warning
        self.user_warnings[user_id].append(time.time())
        warning_count = len(self.user_warnings[user_id])

        # Delete the offending message
        try:
            await message.delete()
        except:
            pass

        # Progressive punishment
        if warning_count == 1:
            await self._send_warning(
                message.channel, user, violation_type, warning_count
            )
        elif warning_count == 2:
            await self._send_warning(
                message.channel, user, violation_type, warning_count
            )
            await self._timeout_user(user, 60)  # 1 minute timeout
        elif warning_count >= 3:
            await self._timeout_user(user, self.config["mute_duration"] * warning_count)
            await self._notify_moderators(
                message.guild, user, violation_type, warning_count
            )

        logger.warning(
            f"Moderation action: {user} - {violation_type} (Warning #{warning_count})"
        )

    async def _send_warning(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        violation_type: str,
        warning_count: int,
    ):
        """Send warning message to user"""
        violation_messages = {
            "spam": "spamming messages",
            "caps_spam": "using excessive capital letters",
            "mention_spam": "mentioning too many users",
            "repeated_content": "sending repeated messages",
        }

        embed = discord.Embed(
            title="⚠️ **Moderation Warning**",
            description=f"{user.mention}, please stop {violation_messages.get(violation_type, 'violating server rules')}.",
            color=0xFF9900,
        )

        embed.add_field(
            name="Warning Count",
            value=f"{warning_count}/{self.config['max_warnings']}",
            inline=True,
        )

        if warning_count >= 2:
            embed.add_field(
                name="Next Violation",
                value="Will result in temporary timeout",
                inline=True,
            )

        embed.set_footer(text="Warnings automatically expire after 1 hour")

        await channel.send(embed=embed, delete_after=30)

    async def _timeout_user(self, user: discord.Member, duration: int):
        """Timeout user for specified duration"""
        try:
            await user.timeout(
                discord.utils.utcnow() + discord.timedelta(seconds=duration)
            )
            self.muted_users.add(user.id)

            # Auto-remove from muted list after timeout
            asyncio.create_task(
                self._remove_from_muted_after_timeout(user.id, duration)
            )

        except Exception as e:
            logger.error(f"Failed to timeout user {user}: {e}")

    async def _remove_from_muted_after_timeout(self, user_id: int, duration: int):
        """Remove user from muted list after timeout expires"""
        await asyncio.sleep(duration)
        self.muted_users.discard(user_id)

    async def _notify_moderators(
        self,
        guild: discord.Guild,
        user: discord.Member,
        violation_type: str,
        warning_count: int,
    ):
        """Notify moderators of repeated violations"""
        # Find moderation channel or general channel
        mod_channel = (
            discord.utils.get(guild.text_channels, name="mod-log")
            or guild.system_channel
        )

        if mod_channel:
            embed = discord.Embed(
                title="🚨 **Repeated Violations**",
                description=f"**User:** {user.mention} ({user})\n**Violation:** {violation_type}\n**Warning Count:** {warning_count}",
                color=0xFF0000,
            )

            embed.set_footer(text="Consider manual review")
            await mod_channel.send(embed=embed)

    def _cleanup_old_warnings(self, user_id: int):
        """Remove warnings older than decay time"""
        current_time = time.time()
        self.user_warnings[user_id] = [
            warning_time
            for warning_time in self.user_warnings[user_id]
            if current_time - warning_time <= self.config["warning_decay"]
        ]

    def get_user_warnings(self, user_id: int) -> int:
        """Get current warning count for user"""
        self._cleanup_old_warnings(user_id)
        return len(self.user_warnings[user_id])

    def get_stats(self) -> Dict:
        """Get moderation statistics"""
        return {
            "active_warnings": sum(
                len(warnings) for warnings in self.user_warnings.values()
            ),
            "muted_users": len(self.muted_users),
            "tracked_users": len(self.message_history),
        }
