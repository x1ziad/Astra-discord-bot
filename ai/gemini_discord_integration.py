"""
Discord Integration for Gemini Image Generation
Handles Discord-specific functionality for image generation
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
import io
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import time

from .gemini_image_generator import (
    GeminiImageGenerator,
    ImageGenerationRequest,
    ImageSize,
    ImageStyle,
    get_gemini_generator,
)

logger = logging.getLogger("astra.gemini_discord")


class GeminiImagePermissions:
    """Handle permissions for image generation"""

    def __init__(self):
        # Default channel for regular users (can be configured)
        self.default_channel_id = 1402666535696470169

        # Rate limits per user role
        self.rate_limits = {
            "admin": {"per_hour": 100, "per_day": 500},
            "mod": {"per_hour": 50, "per_day": 200},
            "user": {"per_hour": 10, "per_day": 50},
        }

        # User request tracking
        self.user_requests: Dict[int, List[datetime]] = {}

    def get_user_role(self, member: discord.Member) -> str:
        """Determine user role for rate limiting"""
        if member.guild_permissions.administrator:
            return "admin"
        elif any(role.permissions.manage_messages for role in member.roles):
            return "mod"
        else:
            return "user"

    def check_channel_permission(
        self, user: discord.Member, channel: discord.TextChannel
    ) -> Tuple[bool, Optional[str]]:
        """Check if user can generate images in this channel"""
        user_role = self.get_user_role(user)

        # Admins and mods can use anywhere
        if user_role in ["admin", "mod"]:
            return True, None

        # Regular users can only use in default channel
        if channel.id != self.default_channel_id:
            return (
                False,
                f"Regular users can only generate images in <#{self.default_channel_id}>",
            )

        return True, None

    def check_rate_limit(
        self, user_id: int, user_role: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if user has exceeded rate limits"""
        now = datetime.now(timezone.utc)

        # Get user's request history
        user_history = self.user_requests.get(user_id, [])

        # Clean old requests (older than 24 hours)
        user_history = [
            req for req in user_history if (now - req).total_seconds() < 86400
        ]

        # Check hourly limit
        recent_requests = [
            req for req in user_history if (now - req).total_seconds() < 3600
        ]
        hourly_limit = self.rate_limits[user_role]["per_hour"]

        if len(recent_requests) >= hourly_limit:
            return (
                False,
                f"Rate limit exceeded: {hourly_limit} images per hour for {user_role}s",
            )

        # Check daily limit
        daily_limit = self.rate_limits[user_role]["per_day"]
        if len(user_history) >= daily_limit:
            return (
                False,
                f"Rate limit exceeded: {daily_limit} images per day for {user_role}s",
            )

        # Update request history
        user_history.append(now)
        self.user_requests[user_id] = user_history

        return True, None


class GeminiImageDiscord:
    """Discord interface for Gemini image generation"""

    def __init__(self):
        self.generator = get_gemini_generator()
        self.permissions = GeminiImagePermissions()
        self.logger = logging.getLogger("astra.gemini_discord")

    async def handle_image_command(
        self,
        interaction: discord.Interaction,
        prompt: str,
        style: str = "realistic",
        size: str = "square_hd",
    ) -> None:
        """
        Handle Discord slash command for image generation

        Args:
            interaction: Discord interaction object
            prompt: Text description for image
            style: Image style (realistic, artistic, etc.)
            size: Image size (square_hd, portrait, etc.)
        """
        try:
            # Defer response to prevent timeout
            await interaction.response.defer()

            # Check if generator is available
            if not self.generator.is_available():
                await self._send_error_embed(
                    interaction,
                    "🚫 Service Unavailable",
                    "Gemini image generation is not available. Please check configuration.",
                    color=0xE74C3C,
                )
                return

            # Check permissions
            permission_ok, permission_error = self.permissions.check_channel_permission(
                interaction.user, interaction.channel
            )
            if not permission_ok:
                await self._send_error_embed(
                    interaction,
                    "🚫 Permission Denied",
                    permission_error,
                    color=0xE74C3C,
                )
                return

            # Check rate limits
            user_role = self.permissions.get_user_role(interaction.user)
            rate_ok, rate_error = self.permissions.check_rate_limit(
                interaction.user.id, user_role
            )
            if not rate_ok:
                await self._send_error_embed(
                    interaction, "⏰ Rate Limited", rate_error, color=0xF39C12
                )
                return

            # Send initial status message
            status_embed = discord.Embed(
                title="🎨 Generating Image with Gemini AI",
                description=f"**Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )
            status_embed.add_field(
                name="⚙️ Settings",
                value=f"**Style:** {style.title()}\n**Size:** {size.replace('_', ' ').title()}\n**Model:** Gemini 2.0",
                inline=True,
            )
            status_embed.add_field(
                name="👤 User",
                value=f"{interaction.user.mention} ({user_role.title()})",
                inline=True,
            )
            status_embed.set_footer(
                text="🤖 Powered by Google Gemini AI • This may take 30-60 seconds"
            )

            status_message = await interaction.followup.send(embed=status_embed)

            # Create generation request
            try:
                size_enum = ImageSize(size.upper())
            except ValueError:
                size_enum = ImageSize.SQUARE_HD

            try:
                style_enum = ImageStyle(style.lower())
            except ValueError:
                style_enum = ImageStyle.REALISTIC

            request = ImageGenerationRequest(
                prompt=prompt,
                user_id=interaction.user.id,
                channel_id=interaction.channel.id,
                guild_id=interaction.guild.id if interaction.guild else None,
                size=size_enum,
                style=style_enum,
            )

            # Generate image
            self.logger.info(
                f"🎨 Starting image generation for user {interaction.user.id}"
            )
            result = await self.generator.generate_image(request)

            if result.success and result.image_data:
                await self._send_success_embed(
                    interaction, status_message, result, prompt, style, size
                )
            else:
                await self._send_error_embed(
                    interaction,
                    "❌ Generation Failed",
                    result.error or "Unknown error occurred",
                    color=0xE74C3C,
                    edit_message=status_message,
                )

        except Exception as e:
            self.logger.error(f"💥 Critical error in image command: {e}", exc_info=True)
            await self._send_error_embed(
                interaction,
                "💥 Critical Error",
                "An unexpected error occurred. Please try again later.",
                color=0x992D22,
            )

    async def _send_success_embed(
        self,
        interaction: discord.Interaction,
        status_message: discord.WebhookMessage,
        result: Any,
        prompt: str,
        style: str,
        size: str,
    ) -> None:
        """Send success embed with generated image"""
        try:
            # Create success embed
            success_embed = discord.Embed(
                title="✅ Image Generated Successfully!",
                description=f"**Prompt:** {prompt[:300]}{'...' if len(prompt) > 300 else ''}",
                color=0x27AE60,
                timestamp=datetime.now(timezone.utc),
            )

            # Add generation details
            success_embed.add_field(
                name="⚡ Performance",
                value=f"🕐 {result.generation_time:.1f}s\n🤖 Gemini 2.0\n✨ Enhanced",
                inline=True,
            )

            success_embed.add_field(
                name="🎯 Settings",
                value=f"🎨 {style.title()}\n📐 {size.replace('_', ' ').title()}\n🖼️ High Quality",
                inline=True,
            )

            success_embed.add_field(
                name="👤 Created by",
                value=f"{interaction.user.mention}\n🏷️ {self.permissions.get_user_role(interaction.user).title()}",
                inline=True,
            )

            # Add AI response if available
            if result.text_response:
                success_embed.add_field(
                    name="🤖 AI Response",
                    value=result.text_response[:500]
                    + ("..." if len(result.text_response) > 500 else ""),
                    inline=False,
                )

            # Create image file
            image_file = discord.File(
                io.BytesIO(result.image_data),
                filename=f"gemini_image_{interaction.user.id}_{int(time.time())}.png",
            )

            success_embed.set_image(url=f"attachment://{image_file.filename}")
            success_embed.set_footer(
                text="🎨 Generated with Google Gemini AI • Use /gemini-image for more!"
            )

            # Edit status message with final result
            await status_message.edit(embed=success_embed, attachments=[image_file])

            self.logger.info(
                f"✅ Image successfully delivered to user {interaction.user.id}"
            )

        except Exception as e:
            self.logger.error(f"❌ Error sending success embed: {e}")
            await self._send_error_embed(
                interaction,
                "⚠️ Display Error",
                "Image was generated but couldn't be displayed properly.",
                color=0xF39C12,
            )

    async def _send_error_embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: int = 0xE74C3C,
        edit_message: Optional[discord.WebhookMessage] = None,
    ) -> None:
        """Send error embed"""
        error_embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # Add helpful suggestions
        if "rate limit" in description.lower():
            error_embed.add_field(
                name="💡 What you can do",
                value="• Wait for your limit to reset\n• Try again later\n• Contact mods for higher limits",
                inline=False,
            )
        elif "permission" in description.lower():
            error_embed.add_field(
                name="📍 Where to use",
                value=f"• Regular users: <#{self.permissions.default_channel_id}>\n• Mods/Admins: Any channel",
                inline=False,
            )
        else:
            error_embed.add_field(
                name="🔄 Try again",
                value="• Use a simpler prompt\n• Check your spelling\n• Wait a moment and retry",
                inline=False,
            )

        error_embed.set_footer(text="Contact support if this issue persists")

        try:
            if edit_message:
                await edit_message.edit(embed=error_embed, attachments=[])
            else:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Failed to send error embed: {e}")

    async def get_status_embed(self) -> discord.Embed:
        """Get status embed for the image generation system"""
        stats = self.generator.get_statistics()

        embed = discord.Embed(
            title="🤖 Gemini Image Generation Status",
            color=0x3498DB if self.generator.is_available() else 0xE74C3C,
            timestamp=datetime.now(timezone.utc),
        )

        # Status
        status = "🟢 Online" if self.generator.is_available() else "🔴 Offline"
        embed.add_field(name="📡 Status", value=status, inline=True)
        embed.add_field(name="🤖 Model", value="Gemini 2.0 Flash", inline=True)
        embed.add_field(name="🏢 Provider", value="Google AI", inline=True)

        # Statistics
        embed.add_field(
            name="📊 Statistics",
            value=f"**Total Requests:** {stats['total_requests']}\n"
            f"**Success Rate:** {stats['success_rate']}\n"
            f"**Avg Time:** {stats['average_generation_time']}",
            inline=True,
        )

        # Rate Limits
        embed.add_field(
            name="⏱️ Current Usage",
            value=f"**This minute:** {stats['rate_limits']['per_minute']}/{stats['rate_limits']['max_per_minute']}\n"
            f"**This hour:** {stats['rate_limits']['per_hour']}/{stats['rate_limits']['max_per_hour']}",
            inline=True,
        )

        # Permissions
        embed.add_field(
            name="🔐 Permissions",
            value=f"**Default Channel:** <#{self.permissions.default_channel_id}>\n"
            f"**Admin:** 100/hr, 500/day\n"
            f"**Mod:** 50/hr, 200/day\n"
            f"**User:** 10/hr, 50/day",
            inline=False,
        )

        embed.set_footer(text="🎨 Powered by Google Gemini AI")

        return embed


# Global instance
_discord_interface: Optional[GeminiImageDiscord] = None


def get_gemini_discord() -> GeminiImageDiscord:
    """Get the global Gemini Discord interface"""
    global _discord_interface
    if _discord_interface is None:
        _discord_interface = GeminiImageDiscord()
    return _discord_interface
