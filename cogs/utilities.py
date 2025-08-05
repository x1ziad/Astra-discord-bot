"""
Utility Commands Cog
Provides helpful utility commands for server management and user convenience
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import time
import hashlib
import base64
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Union
import re
import urllib.parse

from config.enhanced_config import EnhancedConfigManager


class Utilities(commands.Cog):
    """Utility commands for enhanced bot functionality"""

    def __init__(self, bot):
        self.bot = bot
        self.config = EnhancedConfigManager()

    @app_commands.command(name="userinfo", description="👤 Get detailed information about a user")
    @app_commands.describe(user="The user to get information about (defaults to yourself)")
    async def userinfo_command(
        self, 
        interaction: discord.Interaction, 
        user: Optional[discord.Member] = None
    ):
        """Get detailed information about a user"""
        target_user = user or interaction.user
        
        embed = discord.Embed(
            title=f"👤 User Information",
            color=target_user.color if target_user.color != discord.Color.default() else 0x00BFFF,
            timestamp=datetime.now(timezone.utc)
        )

        # Set user avatar as thumbnail
        embed.set_thumbnail(url=target_user.display_avatar.url)

        # Basic information
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Username:** {target_user.name}\n"
                  f"**Display Name:** {target_user.display_name}\n"
                  f"**ID:** `{target_user.id}`\n"
                  f"**Bot:** {'Yes' if target_user.bot else 'No'}",
            inline=True
        )

        # Account information
        created_timestamp = int(target_user.created_at.timestamp())
        if isinstance(target_user, discord.Member) and target_user.joined_at:
            joined_timestamp = int(target_user.joined_at.timestamp())
            
            embed.add_field(
                name="📅 Account Info",
                value=f"**Created:** <t:{created_timestamp}:R>\n"
                      f"**Joined:** <t:{joined_timestamp}:R>\n"
                      f"**Days in Server:** {(datetime.now(timezone.utc) - target_user.joined_at).days}",
                inline=True
            )
        else:
            embed.add_field(
                name="📅 Account Info",
                value=f"**Created:** <t:{created_timestamp}:R>\n"
                      f"**Joined:** Not available\n"
                      f"**Status:** Outside server",
                inline=True
            )

        # Server-specific information (only if it's a member)
        if isinstance(target_user, discord.Member):
            # Status and activity
            status_emoji = {
                discord.Status.online: "🟢",
                discord.Status.idle: "🟡", 
                discord.Status.dnd: "🔴",
                discord.Status.offline: "⚫"
            }
            
            activity_info = "None"
            if target_user.activities:
                activities = []
                for activity in target_user.activities:
                    if isinstance(activity, discord.Game):
                        activities.append(f"🎮 Playing {activity.name}")
                    elif isinstance(activity, discord.Streaming):
                        activities.append(f"📺 Streaming {activity.name}")
                    elif isinstance(activity, discord.Listening):
                        activities.append(f"🎵 Listening to {activity.name}")
                    elif isinstance(activity, discord.Watching):
                        activities.append(f"👀 Watching {activity.name}")
                    elif isinstance(activity, discord.CustomActivity):
                        activities.append(f"💭 {activity.name}")
                
                activity_info = "\n".join(activities[:3])  # Limit to 3 activities

            embed.add_field(
                name="🌐 Status & Activity",
                value=f"**Status:** {status_emoji.get(target_user.status, '❓')} {target_user.status.name.title()}\n"
                      f"**Activity:** {activity_info}",
                inline=False
            )

            # Roles information
            roles = [role.mention for role in sorted(target_user.roles[1:], key=lambda r: r.position, reverse=True)]
            if roles:
                role_text = ", ".join(roles[:10])  # Limit to first 10 roles
                if len(target_user.roles) > 11:  # 10 + @everyone
                    role_text += f" (+{len(target_user.roles) - 11} more)"
            else:
                role_text = "No roles"

            embed.add_field(
                name=f"🎭 Roles [{len(target_user.roles) - 1}]",
                value=role_text,
                inline=False
            )

            # Permissions (for server members)
            key_perms = []
            if target_user.guild_permissions.administrator:
                key_perms.append("👑 Administrator")
            if target_user.guild_permissions.manage_guild:
                key_perms.append("⚙️ Manage Server")
            if target_user.guild_permissions.manage_channels:
                key_perms.append("📝 Manage Channels")
            if target_user.guild_permissions.manage_roles:
                key_perms.append("🎭 Manage Roles")
            if target_user.guild_permissions.kick_members:
                key_perms.append("👢 Kick Members")
            if target_user.guild_permissions.ban_members:
                key_perms.append("🔨 Ban Members")

            if key_perms:
                embed.add_field(
                    name="🔑 Key Permissions",
                    value="\n".join(key_perms[:6]),
                    inline=True
                )

        # Add footer with additional info
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="🏛️ Get detailed information about this server")
    async def serverinfo_command(self, interaction: discord.Interaction):
        """Get detailed information about the current server"""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return

        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🏛️ {guild.name}",
            description=guild.description or "No description set",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc)
        )

        # Server icon
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Basic information
        created_timestamp = int(guild.created_at.timestamp())
        embed.add_field(
            name="📋 Basic Information",
            value=f"**ID:** `{guild.id}`\n"
                  f"**Owner:** <@{guild.owner_id}>\n"
                  f"**Created:** <t:{created_timestamp}:R>\n"
                  f"**Region:** {guild.preferred_locale}",
            inline=True
        )

        # Member statistics
        total_members = guild.member_count
        if total_members:
            # Try to get more detailed member stats if bot has access
            online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
            bot_count = sum(1 for member in guild.members if member.bot)
            human_count = total_members - bot_count
            
            embed.add_field(
                name="👥 Members",
                value=f"**Total:** {total_members:,}\n"
                      f"**Humans:** {human_count:,}\n"
                      f"**Bots:** {bot_count:,}\n"
                      f"**Online:** {online_members:,}",
                inline=True
            )
        else:
            embed.add_field(
                name="👥 Members",
                value="Member count unavailable",
                inline=True
            )

        # Channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        stage_channels = len(guild.stage_channels)
        forum_channels = len([ch for ch in guild.channels if isinstance(ch, discord.ForumChannel)])

        embed.add_field(
            name="📺 Channels",
            value=f"**Text:** {text_channels}\n"
                  f"**Voice:** {voice_channels}\n"
                  f"**Categories:** {categories}\n"
                  f"**Stages:** {stage_channels}\n"
                  f"**Forums:** {forum_channels}",
            inline=True
        )

        # Server features
        features = []
        feature_map = {
            'VERIFIED': '✅ Verified',
            'PARTNERED': '🤝 Discord Partner',
            'COMMUNITY': '🌐 Community Server',
            'DISCOVERABLE': '🔍 Server Discovery',
            'FEATURABLE': '⭐ Featurable',
            'INVITE_SPLASH': '🎨 Invite Splash',
            'VANITY_URL': '🔗 Custom Invite',
            'ANIMATED_ICON': '🎭 Animated Icon',
            'BANNER': '🖼️ Server Banner',
            'COMMERCE': '💰 Commerce Features',
            'NEWS': '📰 News Channels',
            'PREVIEW_ENABLED': '👀 Preview Enabled',
            'MEMBER_VERIFICATION_GATE_ENABLED': '🚪 Membership Screening',
            'WELCOME_SCREEN_ENABLED': '👋 Welcome Screen'
        }

        for feature in guild.features:
            if feature in feature_map:
                features.append(feature_map[feature])

        if features:
            embed.add_field(
                name="✨ Server Features",
                value="\n".join(features[:8]),
                inline=False
            )

        # Security and verification
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low", 
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }

        nsfw_levels = {
            discord.NSFWLevel.default: "Default",
            discord.NSFWLevel.explicit: "Explicit",
            discord.NSFWLevel.safe: "Safe", 
            discord.NSFWLevel.age_restricted: "Age Restricted"
        }

        embed.add_field(
            name="🔒 Security Settings",
            value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}\n"
                  f"**MFA Required:** {'Yes' if guild.mfa_level else 'No'}\n"
                  f"**NSFW Level:** {nsfw_levels.get(guild.nsfw_level, 'Unknown')}\n"
                  f"**Explicit Filter:** {guild.explicit_content_filter.name.title()}",
            inline=True
        )

        # Boost information
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count or 0
        
        embed.add_field(
            name="🚀 Nitro Boost",
            value=f"**Level:** {boost_level}/3\n"
                  f"**Boosts:** {boost_count}\n"
                  f"**Boosters:** {len(guild.premium_subscribers) if guild.premium_subscribers else 0}",
            inline=True
        )

        # Emoji and sticker information
        emoji_count = len(guild.emojis)
        sticker_count = len(guild.stickers)
        animated_emojis = sum(1 for emoji in guild.emojis if emoji.animated)
        static_emojis = emoji_count - animated_emojis

        embed.add_field(
            name="😀 Emojis & Stickers",
            value=f"**Total Emojis:** {emoji_count}\n"
                  f"**Static:** {static_emojis}\n"
                  f"**Animated:** {animated_emojis}\n"
                  f"**Stickers:** {sticker_count}",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="🖼️ Get a user's avatar")
    @app_commands.describe(
        user="The user whose avatar to display (defaults to yourself)",
        size="Avatar size (defaults to 1024)"
    )
    async def avatar_command(
        self, 
        interaction: discord.Interaction, 
        user: Optional[discord.User] = None,
        size: Optional[int] = 1024
    ):
        """Display a user's avatar"""
        target_user = user or interaction.user
        
        # Validate size
        valid_sizes = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        if size not in valid_sizes:
            size = 1024

        embed = discord.Embed(
            title=f"🖼️ {target_user.display_name}'s Avatar",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc)
        )

        # Get avatar URL with specified size
        avatar_url = target_user.display_avatar.with_size(size).url
        embed.set_image(url=avatar_url)

        # Add download links
        formats = ['png', 'jpg', 'webp']
        if target_user.display_avatar.is_animated():
            formats.append('gif')

        links = []
        for fmt in formats:
            url = target_user.display_avatar.with_size(size).with_format(fmt).url
            links.append(f"[{fmt.upper()}]({url})")

        embed.add_field(
            name="📥 Download Links",
            value=" | ".join(links),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Information",
            value=f"**Size:** {size}x{size}px\n"
                  f"**Animated:** {'Yes' if target_user.display_avatar.is_animated() else 'No'}\n"
                  f"**User ID:** `{target_user.id}`",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="timestamp", description="🕒 Generate Discord timestamps")
    @app_commands.describe(
        time_input="Time input (e.g., '2024-01-01 15:30', 'now', 'in 2 hours')",
        format_type="Timestamp display format"
    )
    async def timestamp_command(
        self,
        interaction: discord.Interaction,
        time_input: str,
        format_type: Optional[str] = "f"
    ):
        """Generate Discord timestamps"""
        
        # Format type validation
        valid_formats = {
            't': 'Short Time',
            'T': 'Long Time', 
            'd': 'Short Date',
            'D': 'Long Date',
            'f': 'Short Date/Time',
            'F': 'Long Date/Time',
            'R': 'Relative Time'
        }
        
        if format_type not in valid_formats:
            format_type = 'f'

        try:
            # Parse time input
            if time_input.lower() == 'now':
                target_time = datetime.now(timezone.utc)
            elif time_input.lower().startswith('in '):
                # Parse relative time like "in 2 hours", "in 30 minutes"
                time_str = time_input[3:].strip()
                match = re.match(r'(\d+)\s*(minute|hour|day|week|month|year)s?', time_str.lower())
                if not match:
                    raise ValueError("Invalid relative time format")
                
                amount, unit = match.groups()
                amount = int(amount)
                
                if unit.startswith('minute'):
                    delta = timedelta(minutes=amount)
                elif unit.startswith('hour'):
                    delta = timedelta(hours=amount)
                elif unit.startswith('day'):
                    delta = timedelta(days=amount)
                elif unit.startswith('week'):
                    delta = timedelta(weeks=amount)
                elif unit.startswith('month'):
                    delta = timedelta(days=amount * 30)  # Approximate
                elif unit.startswith('year'):
                    delta = timedelta(days=amount * 365)  # Approximate
                
                target_time = datetime.now(timezone.utc) + delta
            else:
                # Try to parse various date/time formats
                formats_to_try = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d',
                    '%m/%d/%Y %H:%M:%S',
                    '%m/%d/%Y %H:%M',
                    '%m/%d/%Y',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%d/%m/%Y'
                ]
                
                target_time = None
                for fmt in formats_to_try:
                    try:
                        target_time = datetime.strptime(time_input, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue
                
                if target_time is None:
                    raise ValueError("Unable to parse time format")

            # Generate timestamp
            timestamp = int(target_time.timestamp())
            discord_timestamp = f"<t:{timestamp}:{format_type}>"

            embed = discord.Embed(
                title="🕒 Discord Timestamp Generator",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc)
            )

            embed.add_field(
                name="📅 Generated Timestamp",
                value=f"**Display:** {discord_timestamp}\n"
                      f"**Code:** `<t:{timestamp}:{format_type}>`\n"
                      f"**Unix:** `{timestamp}`",
                inline=False
            )

            # Show all format examples
            examples = []
            for fmt, desc in valid_formats.items():
                example_ts = f"<t:{timestamp}:{fmt}>"
                examples.append(f"**{desc} (`{fmt}`):** {example_ts}")

            embed.add_field(
                name="📋 All Format Examples",
                value="\n".join(examples),
                inline=False
            )

            embed.add_field(
                name="ℹ️ Input Information",
                value=f"**Original Input:** `{time_input}`\n"
                      f"**Parsed Time:** {target_time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                      f"**Selected Format:** {valid_formats[format_type]}",
                inline=False
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Timestamp Generation Failed",
                description=f"Unable to parse the time input: `{time_input}`\n\n"
                           f"**Error:** {str(e)}\n\n"
                           f"**Valid formats:**\n"
                           f"• `now` - Current time\n"
                           f"• `in X hours/minutes/days` - Relative time\n"
                           f"• `YYYY-MM-DD HH:MM:SS` - Full datetime\n"
                           f"• `YYYY-MM-DD` - Date only\n"
                           f"• `MM/DD/YYYY` - US date format",
                color=0xFF6B6B,
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="poll", description="📊 Create a poll with multiple options")
    @app_commands.describe(
        question="The poll question",
        option1="First poll option",
        option2="Second poll option", 
        option3="Third poll option (optional)",
        option4="Fourth poll option (optional)",
        option5="Fifth poll option (optional)",
        duration="Poll duration in minutes (default: 60)"
    )
    async def poll_command(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None,
        duration: Optional[int] = 60
    ):
        """Create a poll with reactions"""
        
        # Collect options
        options = [option1, option2]
        if option3: options.append(option3)
        if option4: options.append(option4)
        if option5: options.append(option5)

        # Validate duration
        duration = max(1, min(duration, 1440))  # Between 1 minute and 24 hours

        # Emojis for voting
        reaction_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        embed = discord.Embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc)
        )

        # Add options to embed
        options_text = []
        for i, option in enumerate(options):
            options_text.append(f"{reaction_emojis[i]} {option}")

        embed.add_field(
            name="Options",
            value="\n".join(options_text),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Poll Info",
            value=f"**Duration:** {duration} minutes\n"
                  f"**Created by:** {interaction.user.mention}\n"
                  f"**Ends:** <t:{int((datetime.now(timezone.utc) + timedelta(minutes=duration)).timestamp())}:R>",
            inline=False
        )

        embed.set_footer(text="React with the corresponding emoji to vote!")

        await interaction.response.send_message(embed=embed)
        
        # Get the message to add reactions
        message = await interaction.original_response()
        
        # Add reaction emojis
        for i in range(len(options)):
            await message.add_reaction(reaction_emojis[i])

    @app_commands.command(name="remind", description="⏰ Set a reminder")
    @app_commands.describe(
        time="When to remind you (e.g., '5m', '2h', '1d')",
        message="What to remind you about"
    )
    async def remind_command(
        self,
        interaction: discord.Interaction,
        time: str,
        message: str
    ):
        """Set a personal reminder"""
        
        try:
            # Parse time input
            time = time.lower().strip()
            
            # Extract number and unit
            match = re.match(r'(\d+)\s*([mhd])', time)
            if not match:
                raise ValueError("Invalid time format. Use format like '5m', '2h', '1d'")
            
            amount, unit = match.groups()
            amount = int(amount)
            
            # Convert to seconds
            multipliers = {'m': 60, 'h': 3600, 'd': 86400}
            seconds = amount * multipliers[unit]
            
            # Limit reminder time
            if seconds < 60:  # Minimum 1 minute
                raise ValueError("Reminder must be at least 1 minute")
            if seconds > 604800:  # Maximum 1 week
                raise ValueError("Reminder cannot be longer than 1 week")
            
            # Calculate reminder time
            remind_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
            timestamp = int(remind_time.timestamp())
            
            embed = discord.Embed(
                title="⏰ Reminder Set",
                description=f"I'll remind you about: **{message}**",
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc)
            )
            
            unit_names = {'m': 'minutes', 'h': 'hours', 'd': 'days'}
            embed.add_field(
                name="📅 Reminder Details",
                value=f"**When:** <t:{timestamp}:F>\n"
                      f"**Relative:** <t:{timestamp}:R>\n"
                      f"**Duration:** {amount} {unit_names[unit]}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Wait for the reminder time
            await asyncio.sleep(seconds)
            
            # Send reminder
            reminder_embed = discord.Embed(
                title="⏰ Reminder!",
                description=f"**You asked me to remind you:**\n{message}",
                color=0xFFD700,
                timestamp=datetime.now(timezone.utc)
            )
            
            reminder_embed.add_field(
                name="📅 Originally Set",
                value=f"<t:{int((remind_time - timedelta(seconds=seconds)).timestamp())}:R>",
                inline=True
            )
            
            try:
                await interaction.user.send(embed=reminder_embed)
            except discord.Forbidden:
                # If DM fails, try to reply in the channel
                try:
                    await interaction.followup.send(
                        f"{interaction.user.mention} ⏰ **Reminder:** {message}",
                        embed=reminder_embed
                    )
                except:
                    pass  # If both fail, silently ignore
                    
        except ValueError as e:
            error_embed = discord.Embed(
                title="❌ Invalid Reminder Format",
                description=f"{str(e)}\n\n"
                           f"**Valid formats:**\n"
                           f"• `5m` - 5 minutes\n"
                           f"• `2h` - 2 hours\n"
                           f"• `1d` - 1 day\n\n"
                           f"**Limits:** 1 minute to 1 week",
                color=0xFF6B6B,
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(
                f"❌ **Error setting reminder:** {str(e)}", 
                ephemeral=True
            )


async def setup(bot):
    """Setup function for the utilities cog"""
    await bot.add_cog(Utilities(bot))
