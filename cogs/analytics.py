"""
Server Analytics for Astra Bot
Provides detailed analytics about server activity, user engagement, and trends
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Dict, List, Optional, Any, Tuple
import json
import asyncio
from datetime import datetime, timedelta, time
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from config.config_manager import config_manager
from utils.permissions import has_permission, PermissionLevel


class Analytics(commands.GroupCog, name="analytics"):
    """Server analytics and activity tracking"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

        # Data storage
        self.data_dir = Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Activity tracking
        self.user_activity = self._load_user_activity()
        self.channel_activity = self._load_channel_activity()
        self.daily_stats = self._load_daily_stats()

        # Start background tasks
        self.save_analytics_data.start()
        self.generate_daily_report.start()

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.save_analytics_data.cancel()
        self.generate_daily_report.cancel()

    def _load_user_activity(self) -> Dict[str, Any]:
        """Load user activity data"""
        file_path = self.data_dir / "user_activity.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def _load_channel_activity(self) -> Dict[str, Any]:
        """Load channel activity data"""
        file_path = self.data_dir / "channel_activity.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def _load_daily_stats(self) -> Dict[str, Any]:
        """Load daily statistics"""
        file_path = self.data_dir / "daily_stats.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message activity"""
        if message.author.bot or not message.guild:
            return

        today = datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        channel_id = str(message.channel.id)

        # Track user activity
        if guild_id not in self.user_activity:
            self.user_activity[guild_id] = {}

        if user_id not in self.user_activity[guild_id]:
            self.user_activity[guild_id][user_id] = {
                "username": str(message.author),
                "total_messages": 0,
                "daily_messages": {},
                "channels": {},
                "first_seen": today,
                "last_seen": today,
            }

        user_data = self.user_activity[guild_id][user_id]
        user_data["total_messages"] += 1
        user_data["last_seen"] = today
        user_data["username"] = str(message.author)

        # Daily messages
        if today not in user_data["daily_messages"]:
            user_data["daily_messages"][today] = 0
        user_data["daily_messages"][today] += 1

        # Channel activity
        if channel_id not in user_data["channels"]:
            user_data["channels"][channel_id] = 0
        user_data["channels"][channel_id] += 1

        # Track channel activity
        if guild_id not in self.channel_activity:
            self.channel_activity[guild_id] = {}

        if channel_id not in self.channel_activity[guild_id]:
            self.channel_activity[guild_id][channel_id] = {
                "name": message.channel.name,
                "total_messages": 0,
                "daily_messages": {},
                "users": set(),
            }

        channel_data = self.channel_activity[guild_id][channel_id]
        channel_data["total_messages"] += 1
        channel_data["name"] = message.channel.name

        if today not in channel_data["daily_messages"]:
            channel_data["daily_messages"][today] = 0
        channel_data["daily_messages"][today] += 1

        # Convert set to list for JSON serialization
        if isinstance(channel_data["users"], set):
            channel_data["users"] = list(channel_data["users"])
        if user_id not in channel_data["users"]:
            channel_data["users"].append(user_id)

        # Track daily server stats
        if guild_id not in self.daily_stats:
            self.daily_stats[guild_id] = {}

        if today not in self.daily_stats[guild_id]:
            self.daily_stats[guild_id][today] = {
                "total_messages": 0,
                "active_users": set(),
                "active_channels": set(),
            }

        daily_data = self.daily_stats[guild_id][today]
        daily_data["total_messages"] += 1

        # Convert sets to lists for JSON serialization
        if isinstance(daily_data["active_users"], set):
            daily_data["active_users"] = list(daily_data["active_users"])
        if isinstance(daily_data["active_channels"], set):
            daily_data["active_channels"] = list(daily_data["active_channels"])

        if user_id not in daily_data["active_users"]:
            daily_data["active_users"].append(user_id)
        if channel_id not in daily_data["active_channels"]:
            daily_data["active_channels"].append(channel_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Track voice activity"""
        if member.bot or not member.guild:
            return

        today = datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        guild_id = str(member.guild.id)
        user_id = str(member.id)

        # Initialize user data if needed
        if guild_id not in self.user_activity:
            self.user_activity[guild_id] = {}

        if user_id not in self.user_activity[guild_id]:
            self.user_activity[guild_id][user_id] = {
                "username": str(member),
                "total_messages": 0,
                "daily_messages": {},
                "channels": {},
                "voice_time": {},
                "first_seen": today,
                "last_seen": today,
            }

        user_data = self.user_activity[guild_id][user_id]

        # Track voice activity
        if "voice_time" not in user_data:
            user_data["voice_time"] = {}

        if today not in user_data["voice_time"]:
            user_data["voice_time"][today] = 0

        # This is a simplified voice tracking - in production you'd want more sophisticated time tracking
        if after.channel and not before.channel:
            # User joined voice
            user_data["voice_join_time"] = datetime.now(datetime.UTC).timestamp()
        elif before.channel and not after.channel:
            # User left voice
            if "voice_join_time" in user_data:
                session_time = (
                    datetime.now(datetime.UTC).timestamp() - user_data["voice_join_time"]
                )
                user_data["voice_time"][today] += (
                    session_time / 60
                )  # Convert to minutes
                del user_data["voice_join_time"]

    @app_commands.command(name="overview", description="Get server analytics overview")
    @app_commands.describe(days="Number of days to analyze (default: 7)")
    async def analytics_overview(
        self, interaction: discord.Interaction, days: Optional[int] = 7
    ):
        """Display server analytics overview"""
        if not has_permission(interaction.user, PermissionLevel.MODERATOR):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            guild_id = str(interaction.guild.id)
            end_date = datetime.now(datetime.UTC)
            start_date = end_date - timedelta(days=days)

            stats = self._calculate_overview_stats(guild_id, start_date, end_date)

            embed = discord.Embed(
                title="📊 Server Analytics Overview",
                description=f"Analytics for the last {days} days",
                color=self.config.get_color("primary"),
                timestamp=datetime.now(datetime.UTC),
            )

            # Activity Stats
            embed.add_field(
                name="💬 Message Activity",
                value=f"**Total Messages:** {stats['total_messages']:,}\n"
                f"**Daily Average:** {stats['avg_daily_messages']:,.1f}\n"
                f"**Peak Day:** {stats['peak_day_messages']:,}",
                inline=True,
            )

            # User Stats
            embed.add_field(
                name="👥 User Activity",
                value=f"**Active Users:** {stats['active_users']:,}\n"
                f"**Daily Average:** {stats['avg_daily_users']:,.1f}\n"
                f"**Most Active:** {stats['most_active_user'][:20]}",
                inline=True,
            )

            # Channel Stats
            embed.add_field(
                name="📺 Channel Activity",
                value=f"**Active Channels:** {stats['active_channels']}\n"
                f"**Most Popular:** {stats['most_popular_channel'][:20]}\n"
                f"**Messages:** {stats['top_channel_messages']:,}",
                inline=True,
            )

            # Growth Stats
            embed.add_field(
                name="📈 Growth Trends",
                value=f"**Activity Trend:** {stats['activity_trend']}\n"
                f"**User Growth:** {stats['user_growth']}\n"
                f"**Engagement Rate:** {stats['engagement_rate']:.1f}%",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in analytics overview: {e}")
            await interaction.followup.send("❌ Error generating analytics overview.")

    def _calculate_overview_stats(
        self, guild_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate overview statistics for the given date range"""
        stats = {
            "total_messages": 0,
            "avg_daily_messages": 0,
            "peak_day_messages": 0,
            "active_users": 0,
            "avg_daily_users": 0,
            "most_active_user": "N/A",
            "active_channels": 0,
            "most_popular_channel": "N/A",
            "top_channel_messages": 0,
            "activity_trend": "📊 Stable",
            "user_growth": "📊 Stable",
            "engagement_rate": 0.0,
        }

        if guild_id not in self.daily_stats:
            return stats

        # Analyze daily stats
        daily_messages = []
        daily_users = []
        total_messages = 0
        all_active_users = set()

        for date_str, day_data in self.daily_stats[guild_id].items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= date_obj <= end_date:
                daily_messages.append(day_data["total_messages"])
                daily_users.append(len(day_data["active_users"]))
                total_messages += day_data["total_messages"]
                all_active_users.update(day_data["active_users"])

        if daily_messages:
            stats["total_messages"] = total_messages
            stats["avg_daily_messages"] = sum(daily_messages) / len(daily_messages)
            stats["peak_day_messages"] = max(daily_messages)
            stats["active_users"] = len(all_active_users)
            stats["avg_daily_users"] = (
                sum(daily_users) / len(daily_users) if daily_users else 0
            )

            # Calculate trends
            if len(daily_messages) >= 3:
                recent_avg = sum(daily_messages[-3:]) / 3
                older_avg = (
                    sum(daily_messages[:-3]) / len(daily_messages[:-3])
                    if len(daily_messages) > 3
                    else recent_avg
                )

                if recent_avg > older_avg * 1.1:
                    stats["activity_trend"] = "📈 Increasing"
                elif recent_avg < older_avg * 0.9:
                    stats["activity_trend"] = "📉 Decreasing"

        # Find most active user
        if guild_id in self.user_activity:
            user_messages = {}
            for user_id, user_data in self.user_activity[guild_id].items():
                date_range_messages = 0
                for date_str, count in user_data.get("daily_messages", {}).items():
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if start_date <= date_obj <= end_date:
                        date_range_messages += count
                user_messages[user_data.get("username", "Unknown")] = (
                    date_range_messages
                )

            if user_messages:
                most_active = max(user_messages.items(), key=lambda x: x[1])
                stats["most_active_user"] = most_active[0]

        # Find most popular channel
        if guild_id in self.channel_activity:
            channel_messages = {}
            for channel_id, channel_data in self.channel_activity[guild_id].items():
                date_range_messages = 0
                for date_str, count in channel_data.get("daily_messages", {}).items():
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if start_date <= date_obj <= end_date:
                        date_range_messages += count
                channel_messages[channel_data.get("name", "Unknown")] = (
                    date_range_messages
                )

            if channel_messages:
                most_popular = max(channel_messages.items(), key=lambda x: x[1])
                stats["most_popular_channel"] = most_popular[0]
                stats["top_channel_messages"] = most_popular[1]
                stats["active_channels"] = len(
                    [c for c in channel_messages.values() if c > 0]
                )

        # Calculate engagement rate
        if stats["active_users"] > 0:
            stats["engagement_rate"] = (
                stats["avg_daily_users"] / stats["active_users"]
            ) * 100

        return stats

    @app_commands.command(name="leaderboard", description="Show most active users")
    @app_commands.describe(
        timeframe="Time period to analyze", limit="Number of users to show"
    )
    async def user_leaderboard(
        self,
        interaction: discord.Interaction,
        timeframe: Optional[str] = "week",
        limit: Optional[int] = 10,
    ):
        """Display user activity leaderboard"""
        await interaction.response.defer(thinking=True)

        try:
            guild_id = str(interaction.guild.id)

            # Calculate date range
            end_date = datetime.now(datetime.UTC)
            if timeframe.lower() == "day":
                start_date = end_date - timedelta(days=1)
            elif timeframe.lower() == "week":
                start_date = end_date - timedelta(days=7)
            elif timeframe.lower() == "month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=7)

            leaderboard_data = self._get_user_leaderboard(
                guild_id, start_date, end_date, limit
            )

            embed = discord.Embed(
                title=f"🏆 User Activity Leaderboard - {timeframe.title()}",
                description=f"Most active users in the last {timeframe}",
                color=self.config.get_color("primary"),
                timestamp=datetime.now(datetime.UTC),
            )

            if leaderboard_data:
                leaderboard_text = ""
                medals = ["🥇", "🥈", "🥉"]

                for i, (username, messages, voice_time) in enumerate(leaderboard_data):
                    medal = medals[i] if i < 3 else f"{i+1}."
                    voice_text = f" | {voice_time:.0f}m voice" if voice_time > 0 else ""
                    leaderboard_text += f"{medal} **{username[:20]}** - {messages:,} messages{voice_text}\n"

                embed.add_field(name="Top Users", value=leaderboard_text, inline=False)
            else:
                embed.add_field(
                    name="No Data",
                    value="No activity data found for this period.",
                    inline=False,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in user leaderboard: {e}")
            await interaction.followup.send("❌ Error generating leaderboard.")

    def _get_user_leaderboard(
        self, guild_id: str, start_date: datetime, end_date: datetime, limit: int
    ) -> List[Tuple[str, int, float]]:
        """Get user leaderboard data for the specified date range"""
        if guild_id not in self.user_activity:
            return []

        user_stats = []

        for user_id, user_data in self.user_activity[guild_id].items():
            messages_count = 0
            voice_time = 0.0

            # Count messages in date range
            for date_str, count in user_data.get("daily_messages", {}).items():
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if start_date <= date_obj <= end_date:
                        messages_count += count
                except ValueError:
                    continue

            # Count voice time in date range
            for date_str, time_minutes in user_data.get("voice_time", {}).items():
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if start_date <= date_obj <= end_date:
                        voice_time += time_minutes
                except ValueError:
                    continue

            if messages_count > 0 or voice_time > 0:
                user_stats.append(
                    (user_data.get("username", "Unknown"), messages_count, voice_time)
                )

        # Sort by messages (primary) and voice time (secondary)
        user_stats.sort(key=lambda x: (x[1], x[2]), reverse=True)

        return user_stats[:limit]

    @tasks.loop(minutes=30)
    async def save_analytics_data(self):
        """Periodically save analytics data to files"""
        try:
            # Save user activity
            with open(self.data_dir / "user_activity.json", "w") as f:
                json.dump(self.user_activity, f, indent=2)

            # Save channel activity
            with open(self.data_dir / "channel_activity.json", "w") as f:
                json.dump(self.channel_activity, f, indent=2)

            # Save daily stats
            with open(self.data_dir / "daily_stats.json", "w") as f:
                json.dump(self.daily_stats, f, indent=2)

            self.logger.info("Analytics data saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving analytics data: {e}")

    @tasks.loop(time=time(0, 0))  # Run at midnight UTC
    async def generate_daily_report(self):
        """Generate daily analytics reports"""
        try:
            yesterday = (datetime.now(datetime.UTC) - timedelta(days=1)).strftime("%Y-%m-%d")

            # Generate reports for all guilds
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                if (
                    guild_id in self.daily_stats
                    and yesterday in self.daily_stats[guild_id]
                ):
                    await self._generate_guild_daily_report(guild, yesterday)

        except Exception as e:
            self.logger.error(f"Error generating daily reports: {e}")

    async def _generate_guild_daily_report(self, guild: discord.Guild, date: str):
        """Generate daily report for a specific guild"""
        try:
            guild_id = str(guild.id)
            day_data = self.daily_stats[guild_id][date]

            # Create report
            report = {
                "date": date,
                "guild_name": guild.name,
                "guild_id": guild_id,
                "total_messages": day_data["total_messages"],
                "active_users": len(day_data["active_users"]),
                "active_channels": len(day_data["active_channels"]),
                "generated_at": datetime.now(datetime.UTC).isoformat(),
            }

            # Save report
            reports_dir = self.data_dir / "daily_reports"
            reports_dir.mkdir(exist_ok=True)

            report_file = reports_dir / f"{guild_id}_{date}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error generating daily report for {guild.name}: {e}")


async def setup(bot):
    await bot.add_cog(Analytics(bot))
