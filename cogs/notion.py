"""
Notion integration for Astra Bot
Provides task management, reminders, and notes via Notion API
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any, Union
from pathlib import Path

from config.config_manager import config_manager


class Notion(commands.GroupCog, name="notion"):
    """Notion integration commands for task management and reminders"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

        # API tokens
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")

        # Cache directory
        self.cache_dir = Path("temp/notion_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "events_cache.json"

        # Event data
        self.cached_events = []
        self.last_fetch = None

        # Start background task if enabled
        if (
            self.notion_token
            and self.notion_database_id
            and self.config.is_feature_enabled("notion_integration")
        ):
            self.sync_notion_data.start()
            self.logger.info("Started Notion sync task")
        else:
            self.logger.info(
                "Notion integration disabled: Missing API tokens or feature disabled"
            )

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if hasattr(self, "sync_notion_data") and self.sync_notion_data.is_running():
            self.sync_notion_data.cancel()

    @tasks.loop(minutes=30)
    async def sync_notion_data(self):
        """Background task to fetch data from Notion API"""
        if not self.notion_token or not self.notion_database_id:
            return

        if not self.config.is_feature_enabled("notion_integration"):
            return

        self.logger.info("Syncing data from Notion API...")

        try:
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }

            query_url = (
                f"https://api.notion.com/v1/databases/{self.notion_database_id}/query"
            )

            filter_data = {
                "filter": {
                    "and": [
                        {
                            "property": "Date",
                            "date": {"after": datetime.now().isoformat()},
                        },
                        {
                            "property": "Date",
                            "date": {
                                "before": (
                                    datetime.now() + timedelta(days=30)
                                ).isoformat()
                            },
                        },
                    ]
                },
                "sorts": [{"property": "Date", "direction": "ascending"}],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    query_url, headers=headers, json=filter_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cached_events = self.parse_notion_events(
                            data.get("results", [])
                        )
                        self.last_fetch = datetime.now()

                        # Save to cache file
                        try:
                            with open(self.cache_file, "w") as f:
                                json.dump(
                                    {
                                        "timestamp": self.last_fetch.isoformat(),
                                        "events": self.cached_events,
                                    },
                                    f,
                                    indent=2,
                                )
                        except Exception as e:
                            self.logger.error(f"Failed to save Notion cache: {e}")

                    else:
                        response_text = await response.text()
                        self.logger.error(
                            f"Notion API error ({response.status}): {response_text}"
                        )

        except Exception as e:
            self.logger.error(f"Error fetching Notion data: {e}")
            # Try to load from cache if API request fails
            self._load_from_cache()

    @sync_notion_data.before_loop
    async def before_sync_notion_data(self):
        """Wait for the bot to be ready before starting the task"""
        await self.bot.wait_until_ready()
        # Try to load from cache initially
        self._load_from_cache()

    def _load_from_cache(self):
        """Load events from cache file if it exists"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)
                    self.cached_events = cache_data.get("events", [])
                    self.last_fetch = datetime.fromisoformat(
                        cache_data.get("timestamp", datetime.now().isoformat())
                    )
                    self.logger.info(
                        f"Loaded {len(self.cached_events)} events from cache"
                    )
        except Exception as e:
            self.logger.error(f"Failed to load Notion cache: {e}")

    def parse_notion_events(self, results):
        """Parse the event data from Notion API response"""
        events = []
        for result in results:
            try:
                properties = result.get("properties", {})
                title = self.get_notion_title(properties.get("Name", {}))
                date = self.get_notion_date(properties.get("Date", {}))
                description = self.get_notion_text(properties.get("Description", {}))
                type_tag = self.get_notion_select(properties.get("Type", {}))

                if title and date:
                    events.append(
                        {
                            "title": title,
                            "date": date,
                            "description": description or "No description available",
                            "type": type_tag or "General",
                            "notion_url": result.get("url", ""),
                        }
                    )
            except Exception as e:
                self.logger.error(f"Error parsing Notion event: {e}")
                continue
        return events

    def get_notion_title(self, title_property):
        """Extract title from Notion property"""
        try:
            if title_property.get("type") == "title":
                title_array = title_property.get("title", [])
                if title_array:
                    return title_array[0].get("text", {}).get("content", "")
        except:
            pass
        return None

    def get_notion_date(self, date_property):
        """Extract date from Notion property"""
        try:
            if date_property.get("type") == "date":
                date_obj = date_property.get("date")
                if date_obj:
                    return date_obj.get("start")
        except:
            pass
        return None

    def get_notion_text(self, text_property):
        """Extract text from Notion property"""
        try:
            if text_property.get("type") == "rich_text":
                text_array = text_property.get("rich_text", [])
                if text_array:
                    return text_array[0].get("text", {}).get("content", "")
        except:
            pass
        return None

    def get_notion_select(self, select_property):
        """Extract select value from Notion property"""
        try:
            if select_property.get("type") == "select":
                select_obj = select_property.get("select")
                if select_obj:
                    return select_obj.get("name")
        except:
            pass
        return None

    @app_commands.command(
        name="reminders", description="Show upcoming events and reminders from Notion"
    )
    @app_commands.checks.cooldown(1, 10)
    async def reminders_command(self, interaction: discord.Interaction):
        """Show upcoming events and reminders from Notion"""
        if not self.notion_token or not self.notion_database_id:
            embed = discord.Embed(
                title="⚠️ Notion Integration Not Configured",
                description="Notion integration requires setup. Contact an administrator.",
                color=self.config.get_color("warning"),
            )
            embed.add_field(
                name="📝 Setup Required",
                value="1. Get a Notion API token\n2. Create a database\n3. Add tokens to `.env` file",
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Show loading state
        await interaction.response.defer()

        # If there are no cached events, try to fetch them now
        if not self.cached_events:
            try:
                # Only fetch if we haven't tried recently
                if self.last_fetch is None or (
                    datetime.now() - self.last_fetch
                ) > timedelta(minutes=5):
                    await self.sync_notion_data()
            except Exception as e:
                self.logger.error(f"Failed to fetch events on demand: {e}")

            if not self.cached_events:
                await interaction.followup.send(
                    "No upcoming events found in Notion database."
                )
                return

        # Create embed with upcoming events
        embed = discord.Embed(
            title="📅 Upcoming Events & Reminders",
            description="Here's a list of upcoming events synced from Notion.",
            color=self.config.get_color("info"),
            timestamp=datetime.now(timezone.utc),
        )

        # Add upcoming events to embed
        for event in self.cached_events[:5]:  # Show first 5 events
            event_date = event["date"]
            if "T" in event_date:  # If date includes time
                try:
                    dt = datetime.fromisoformat(event_date)
                    formatted_date = f"<t:{int(dt.timestamp())}:F>"
                except:
                    formatted_date = event_date
            else:
                formatted_date = event_date

            embed.add_field(
                name=f"📌 {event['title']}",
                value=(
                    f"**When:** {formatted_date}\n"
                    f"**Type:** {event['type']}\n"
                    f"**Details:** {event['description'][:150]}{'...' if len(event['description']) > 150 else ''}\n"
                    f"[View in Notion]({event['notion_url']})"
                ),
                inline=False,
            )

        # Add count of remaining events if there are more
        if len(self.cached_events) > 5:
            embed.add_field(
                name="➕ More Events",
                value=f"There are {len(self.cached_events) - 5} more upcoming events not shown here.",
                inline=False,
            )

        # Add last updated time
        if self.last_fetch:
            embed.set_footer(
                text=f"Last updated: {self.last_fetch.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sync", description="Force a sync with Notion")
    @app_commands.default_permissions(administrator=True)
    async def sync_notion_command(self, interaction: discord.Interaction):
        """Force a sync with Notion (Admin only)"""
        if not self.notion_token or not self.notion_database_id:
            await interaction.response.send_message(
                "⚠️ Notion integration is not configured. Add API tokens to .env file.",
                ephemeral=True,
            )
            return

        # Show loading state
        await interaction.response.defer(ephemeral=True)

        try:
            # Force a sync
            previous_count = len(self.cached_events)
            await self.sync_notion_data()
            new_count = len(self.cached_events)

            # Send success message
            embed = discord.Embed(
                title="✅ Notion Sync Complete",
                description=f"Successfully synced {new_count} events from Notion.",
                color=self.config.get_color("success"),
                timestamp=datetime.now(timezone.utc),
            )

            if previous_count != new_count:
                embed.add_field(
                    name="📊 Changes",
                    value=f"Previous: {previous_count} events\nNew: {new_count} events",
                    inline=True,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            # Send error message
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"An error occurred while syncing with Notion:\n```\n{str(e)}\n```",
                color=self.config.get_color("error"),
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.followup.send(embed=embed)
            self.logger.error(f"Manual Notion sync failed: {e}")

    @app_commands.command(name="status", description="Check Notion integration status")
    @app_commands.default_permissions(administrator=True)
    async def notion_status_command(self, interaction: discord.Interaction):
        """Check Notion integration status (Admin only)"""
        # Create status embed
        embed = discord.Embed(
            title="📊 Notion Integration Status",
            color=self.config.get_color("info"),
            timestamp=datetime.now(timezone.utc),
        )

        # Check token configuration
        token_status = "✅ Configured" if self.notion_token else "❌ Not configured"
        database_status = (
            "✅ Configured" if self.notion_database_id else "❌ Not configured"
        )

        embed.add_field(
            name="🔑 API Configuration",
            value=f"**API Token:** {token_status}\n**Database ID:** {database_status}",
            inline=False,
        )

        # Check feature enabled status
        feature_enabled = self.config.is_feature_enabled("notion_integration")
        embed.add_field(
            name="⚙️ Feature Status",
            value="✅ Enabled" if feature_enabled else "❌ Disabled",
            inline=True,
        )

        # Check sync status
        task_status = (
            "✅ Running"
            if hasattr(self, "sync_notion_data") and self.sync_notion_data.is_running()
            else "❌ Stopped"
        )

        last_fetch_str = (
            f"<t:{int(self.last_fetch.timestamp())}:R>" if self.last_fetch else "Never"
        )

        embed.add_field(
            name="🔄 Sync Status",
            value=f"**Task:** {task_status}\n**Last Sync:** {last_fetch_str}\n**Cached Events:** {len(self.cached_events)}",
            inline=True,
        )

        # Add troubleshooting info
        if not self.notion_token or not self.notion_database_id:
            embed.add_field(
                name="🔧 Troubleshooting",
                value="1. Add `NOTION_TOKEN` and `NOTION_DATABASE_ID` to your `.env` file\n"
                "2. Make sure your API token has access to the database\n"
                "3. Enable the feature with `/admin config features.notion_integration.enabled true`\n"
                "4. Restart the bot",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Notion(bot))
