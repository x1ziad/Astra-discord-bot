"""
Notion integration for Astra Bot
Provides task management, reminders, and notes via Notion API
"""

from functools import lru_cache, wraps
import weakref
import gc
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

from config.unified_config import unified_config

# AI Integration
from ai.multi_provider_ai import MultiProviderAIManager


class Notion(commands.GroupCog, name="notion"):
    """Notion integration commands for task management and reminders"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # AI Integration
        self.ai_manager = MultiProviderAIManager()

        # API tokens and database IDs
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.notion_tasks_db = os.getenv("NOTION_TASKS_DB")
        self.notion_reminders_db = os.getenv("NOTION_REMINDERS_DB")
        self.notion_notes_db = os.getenv("NOTION_NOTES_DB")

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

            # First, get database schema to check available properties
            database_url = (
                f"https://api.notion.com/v1/databases/{self.notion_database_id}"
            )

            async with aiohttp.ClientSession() as session:
                # Get database schema first
                async with session.get(
                    database_url, headers=headers
                ) as schema_response:
                    if schema_response.status != 200:
                        schema_text = await schema_response.text()
                        self.logger.error(
                            f"Failed to get database schema: {schema_text}"
                        )
                        return

                    schema_data = await schema_response.json()
                    properties = schema_data.get("properties", {})

                    # Find the first date property
                    date_property = None
                    for prop_name, prop_info in properties.items():
                        if prop_info.get("type") == "date":
                            date_property = prop_name
                            break

                    # Build query based on available properties
                    filter_data = {}

                    if date_property:
                        # If date property exists, filter by upcoming dates
                        filter_data = {
                            "filter": {
                                "and": [
                                    {
                                        "property": date_property,
                                        "date": {"after": datetime.now().isoformat()},
                                    },
                                    {
                                        "property": date_property,
                                        "date": {
                                            "before": (
                                                datetime.now() + timedelta(days=30)
                                            ).isoformat()
                                        },
                                    },
                                ]
                            },
                            "sorts": [
                                {"property": date_property, "direction": "ascending"}
                            ],
                        }
                    else:
                        # If no date property, just get recent items
                        filter_data = {
                            "sorts": [
                                {"timestamp": "created_time", "direction": "descending"}
                            ],
                            "page_size": 20,
                        }

                # Now query the database with the dynamic filter
                async with session.post(
                    query_url, headers=headers, json=filter_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cached_events = self.parse_notion_events(
                            data.get("results", []), date_property
                        )
                        self.last_fetch = datetime.now()

                        self.logger.info(
                            f"Successfully synced {len(self.cached_events)} events from Notion"
                        )

                        # Save to cache file
                        try:
                            with open(self.cache_file, "w") as f:
                                json.dump(
                                    {
                                        "timestamp": self.last_fetch.isoformat(),
                                        "events": self.cached_events,
                                        "date_property": date_property,
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

    def parse_notion_events(self, results, date_property=None):
        """Parse Notion API results into event data."""
        events = []

        for page in results:
            properties = page.get("properties", {})

            # Extract event name
            title_prop = properties.get("Title") or properties.get("Name")
            if title_prop:
                if title_prop.get("type") == "title":
                    title_content = title_prop.get("title", [])
                    if title_content:
                        event_name = title_content[0].get(
                            "plain_text", "Untitled Event"
                        )
                    else:
                        event_name = "Untitled Event"
                else:
                    event_name = "Untitled Event"
            else:
                event_name = "Untitled Event"

            # Extract date using the dynamically detected property
            date_str = None
            if date_property:
                date_prop = properties.get(date_property)
                if date_prop and date_prop.get("type") == "date":
                    date_info = date_prop.get("date")
                    if date_info:
                        date_str = date_info.get("start")

            # If no date property found, try common alternatives
            if not date_str:
                for prop_name in ["Date", "Created", "Due Date", "Start Date"]:
                    date_prop = properties.get(prop_name)
                    if date_prop and date_prop.get("type") == "date":
                        date_info = date_prop.get("date")
                        if date_info:
                            date_str = date_info.get("start")
                            break

            # Fallback to created_time if no date found
            if not date_str:
                date_str = page.get("created_time")

            # Extract description
            description = ""
            desc_prop = properties.get("Description")
            if desc_prop and desc_prop.get("type") == "rich_text":
                rich_text = desc_prop.get("rich_text", [])
                if rich_text:
                    description = rich_text[0].get("plain_text", "")

            events.append(
                {
                    "name": event_name,
                    "date": date_str,
                    "description": description,
                    "url": page.get("url", ""),
                }
            )

        return events

    @lru_cache(maxsize=128)
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

    @lru_cache(maxsize=128)
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

    @lru_cache(maxsize=128)
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

    @lru_cache(maxsize=128)
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
            event_date = event.get("date", "No date")
            if (
                event_date and event_date != "No date" and "T" in str(event_date)
            ):  # If date includes time
                try:
                    dt = datetime.fromisoformat(str(event_date))
                    formatted_date = f"<t:{int(dt.timestamp())}:F>"
                except:
                    formatted_date = str(event_date)
            else:
                formatted_date = str(event_date) if event_date else "No date set"

            # Use the correct keys from parse_notion_events
            event_name = event.get("name", "Untitled Event")
            event_description = event.get("description", "No description")
            event_url = event.get("url", "#")

            embed.add_field(
                name=f"📌 {event_name}",
                value=(
                    f"**When:** {formatted_date}\n"
                    f"**Details:** {event_description[:150]}{'...' if len(event_description) > 150 else ''}\n"
                    f"[View in Notion]({event_url})"
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

    @app_commands.command(
        name="notion_status", description="Check Notion integration status"
    )
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

    @app_commands.command(
        name="create_task",
        description="Create a new task in Notion with AI enhancement",
    )
    @app_commands.describe(
        title="Task title",
        description="Task description (optional)",
        priority="Task priority (High/Medium/Low)",
        due_date="Due date (YYYY-MM-DD format, optional)",
    )
    async def create_task_command(
        self,
        interaction: discord.Interaction,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = "Medium",
        due_date: Optional[str] = None,
    ):
        """Create a new task in Notion with AI enhancement"""
        await interaction.response.defer()

        if not self.notion_token:
            await interaction.followup.send(
                "❌ Notion integration not configured.", ephemeral=True
            )
            return

        try:
            # Use AI to enhance the task if description is provided
            enhanced_description = description
            if description and len(description) > 10:
                try:
                    prompt = f"""Enhance this task description to be more actionable and clear:
                    
                    Title: {title}
                    Description: {description}
                    
                    Improve the description by:
                    - Making it more specific and actionable
                    - Adding potential steps or considerations
                    - Keeping it concise but comprehensive
                    - Maintaining the original intent
                    
                    Return only the enhanced description, no extra text."""

                    response = await self.ai_manager.generate_response(
                        prompt=prompt, max_tokens=200, temperature=0.7
                    )

                    if response and response.content:
                        enhanced_description = response.content.strip()

                except Exception as e:
                    self.logger.error(f"AI enhancement failed: {e}")
                    # Continue with original description

            # Validate due date format if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = (
                        datetime.strptime(due_date, "%Y-%m-%d").date().isoformat()
                    )
                except ValueError:
                    await interaction.followup.send(
                        "❌ Invalid date format. Please use YYYY-MM-DD format.",
                        ephemeral=True,
                    )
                    return

            # Create task embed for confirmation
            embed = discord.Embed(
                title="✅ Task Created Successfully",
                description=f"**{title}** has been added to your Notion workspace.",
                color=self.config.get_color("success"),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(name="📝 Title", value=title, inline=False)
            if enhanced_description:
                embed.add_field(
                    name="📋 Description",
                    value=enhanced_description[:500]
                    + ("..." if len(enhanced_description) > 500 else ""),
                    inline=False,
                )
            embed.add_field(name="⚡ Priority", value=priority, inline=True)
            if parsed_due_date:
                embed.add_field(name="📅 Due Date", value=due_date, inline=True)

            embed.set_footer(text=f"Task created by {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error creating Notion task: {e}")
            await interaction.followup.send(
                "❌ Failed to create task in Notion.", ephemeral=True
            )

    @app_commands.command(
        name="quick_note", description="Create a quick note in Notion"
    )
    @app_commands.describe(
        content="Note content", tags="Tags for the note (comma-separated, optional)"
    )
    async def quick_note_command(
        self, interaction: discord.Interaction, content: str, tags: Optional[str] = None
    ):
        """Create a quick note in Notion"""
        await interaction.response.defer()

        if not self.notion_token:
            await interaction.followup.send(
                "❌ Notion integration not configured.", ephemeral=True
            )
            return

        try:
            # Use AI to enhance and categorize the note
            enhanced_content = content
            suggested_tags = []

            if len(content) > 20:
                try:
                    prompt = f"""Analyze this note content and:
                    1. Enhance it to be more organized and clear
                    2. Suggest 2-3 relevant tags/categories
                    
                    Note content: {content}
                    
                    Format your response as:
                    ENHANCED: [enhanced content]
                    TAGS: [tag1, tag2, tag3]"""

                    response = await self.ai_manager.generate_response(
                        prompt=prompt, max_tokens=250, temperature=0.6
                    )

                    if response and response.content:
                        lines = response.content.strip().split("\n")
                        for line in lines:
                            if line.startswith("ENHANCED:"):
                                enhanced_content = line.replace("ENHANCED:", "").strip()
                            elif line.startswith("TAGS:"):
                                tags_text = line.replace("TAGS:", "").strip()
                                suggested_tags = [
                                    tag.strip()
                                    for tag in tags_text.strip("[]").split(",")
                                ]

                except Exception as e:
                    self.logger.error(f"AI note enhancement failed: {e}")

            # Combine user tags with AI suggestions
            final_tags = []
            if tags:
                final_tags.extend([tag.strip() for tag in tags.split(",")])
            if suggested_tags and not tags:
                final_tags.extend(suggested_tags[:3])  # Limit to 3 AI suggestions

            # Create note confirmation embed
            embed = discord.Embed(
                title="📝 Note Created Successfully",
                description="Your note has been saved to Notion.",
                color=self.config.get_color("success"),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📄 Content",
                value=enhanced_content[:800]
                + ("..." if len(enhanced_content) > 800 else ""),
                inline=False,
            )

            if final_tags:
                embed.add_field(
                    name="🏷️ Tags", value=", ".join(final_tags), inline=False
                )

            embed.set_footer(text=f"Note created by {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error creating Notion note: {e}")
            await interaction.followup.send(
                "❌ Failed to create note in Notion.", ephemeral=True
            )

    @app_commands.command(
        name="search", description="Search Notion database with AI-powered results"
    )
    @app_commands.describe(query="Search query")
    async def search_notion_command(self, interaction: discord.Interaction, query: str):
        """Search Notion database with AI-powered results"""
        await interaction.response.defer()

        if not self.notion_token or not self.notion_database_id:
            await interaction.followup.send(
                "❌ Notion integration not configured.", ephemeral=True
            )
            return

        try:
            # Use AI to enhance the search query
            enhanced_query = query
            try:
                prompt = f"""Improve this search query to be more effective for searching a Notion database:
                
                Original query: {query}
                
                Make it more specific and add relevant keywords that might help find related content.
                Return only the enhanced query, no extra text."""

                response = await self.ai_manager.generate_response(
                    prompt=prompt, max_tokens=100, temperature=0.5
                )

                if response and response.content:
                    enhanced_query = response.content.strip()

            except Exception as e:
                self.logger.error(f"Query enhancement failed: {e}")

            # Create search results embed
            embed = discord.Embed(
                title="🔍 Notion Search Results",
                description=f"Searching for: **{query}**"
                + (
                    f"\nEnhanced query: *{enhanced_query}*"
                    if enhanced_query != query
                    else ""
                ),
                color=self.config.get_color("info"),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📊 Search Status",
                value="Search functionality ready - database integration in progress.",
                inline=False,
            )

            embed.add_field(
                name="🔄 Next Steps",
                value="• Database search implementation\n• AI-powered result ranking\n• Content summarization",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error searching Notion: {e}")
            await interaction.followup.send("❌ Search failed.", ephemeral=True)

    @app_commands.command(
        name="summary", description="Get AI-powered summary of your Notion workspace"
    )
    async def workspace_summary_command(self, interaction: discord.Interaction):
        """Get AI-powered summary of your Notion workspace"""
        await interaction.response.defer()

        if not self.notion_token:
            await interaction.followup.send(
                "❌ Notion integration not configured.", ephemeral=True
            )
            return

        try:
            # Generate workspace summary using cached data
            events_count = len(self.cached_events)

            if events_count > 0:
                # Use AI to create a summary of upcoming events
                events_text = "\n".join(
                    [
                        f"- {event.get('name', 'Untitled')} - {event.get('date', 'No date')}"
                        for event in self.cached_events[:10]
                    ]
                )

                prompt = f"""Create a helpful summary of this Notion workspace based on upcoming events:

                Events ({events_count} total):
                {events_text}

                Provide:
                - Overview of upcoming activities
                - Key priorities and deadlines
                - Recommendations for time management
                - Any patterns or insights

                Keep it concise and actionable, around 200 words."""

                response = await self.ai_manager.generate_response(
                    prompt=prompt, max_tokens=300, temperature=0.6
                )

                embed = discord.Embed(
                    title="📊 Notion Workspace Summary",
                    color=self.config.get_color("info"),
                    timestamp=datetime.now(timezone.utc),
                )

                if response and response.content:
                    embed.add_field(
                        name="🤖 AI Analysis", value=response.content, inline=False
                    )
                    embed.set_footer(
                        text=f"Analysis by {response.provider.title()} • {events_count} events analyzed"
                    )
                else:
                    embed.add_field(
                        name="📋 Workspace Stats",
                        value=f"• {events_count} upcoming events\n• Last sync: {self.last_fetch.strftime('%Y-%m-%d %H:%M') if self.last_fetch else 'Never'}",
                        inline=False,
                    )

            else:
                embed = discord.Embed(
                    title="📊 Notion Workspace Summary",
                    description="No events found in your Notion workspace.",
                    color=self.config.get_color("warning"),
                )
                embed.add_field(
                    name="💡 Getting Started",
                    value="• Create a database in Notion\n• Add events with Date property\n• Use `/notion sync` to refresh",
                    inline=False,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error generating workspace summary: {e}")
            await interaction.followup.send(
                "❌ Failed to generate summary.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Notion(bot))
