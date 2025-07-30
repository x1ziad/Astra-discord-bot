import discord
from discord.ext import commands, tasks
import aiohttp
import os
from datetime import datetime, timedelta
import json

class Notion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        
        # Cache for Notion data
        self.cached_events = []
        self.last_fetch = None
        
        # Start background task if token is available
        if self.notion_token and self.notion_database_id:
            self.fetch_notion_data.start()

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if hasattr(self, 'fetch_notion_data'):
            self.fetch_notion_data.cancel()

    @tasks.loop(minutes=30)  # Update every 30 minutes
    async def fetch_notion_data(self):
        """Background task to fetch data from Notion"""
        if not self.notion_token or not self.notion_database_id:
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            # Query the database
            query_url = f"https://api.notion.com/v1/databases/{self.notion_database_id}/query"
            
            # Filter for upcoming events (next 30 days)
            filter_data = {
                "filter": {
                    "and": [
                        {
                            "property": "Date",
                            "date": {
                                "after": datetime.now().isoformat()
                            }
                        },
                        {
                            "property": "Date", 
                            "date": {
                                "before": (datetime.now() + timedelta(days=30)).isoformat()
                            }
                        }
                    ]
                },
                "sorts": [
                    {
                        "property": "Date",
                        "direction": "ascending"
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(query_url, headers=headers, json=filter_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cached_events = self.parse_notion_events(data.get("results", []))
                        self.last_fetch = datetime.now()
                    else:
                        print(f"Notion API error: {response.status}")
                        
        except Exception as e:
            print(f"Error fetching Notion data: {e}")

    def parse_notion_events(self, results):
        """Parse Notion database results into event objects"""
        events = []
        
        for result in results:
            try:
                properties = result.get("properties", {})
                
                # Extract event data (adjust property names based on your Notion database)
                title = self.get_notion_title(properties.get("Name", {}))
                date = self.get_notion_date(properties.get("Date", {}))
                description = self.get_notion_text(properties.get("Description", {}))
                type_tag = self.get_notion_select(properties.get("Type", {}))
                
                if title and date:
                    events.append({
                        "title": title,
                        "date": date,
                        "description": description or "No description available",
                        "type": type_tag or "General",
                        "notion_url": result.get("url", "")
                    })
                    
            except Exception as e:
                print(f"Error parsing Notion event: {e}")
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

    @commands.command(name="reminders")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def show_reminders(self, ctx):
        """Show upcoming events and reminders from Notion"""
        
        if not self.notion_token or not self.notion_database_id:
            embed = discord.Embed(
                title="⚠️ Notion Integration Not Configured",
                description="Notion integration requires setup. Contact an administrator.",
                color=0xff9900
            )
            embed.add_field(
                name="📝 Setup Required",
                value="1. Get a Notion API token\n2. Create a database\n3. Add tokens to `.env` file"
            )

        for event in self.cached_events:
            embed.add_field(
                name=f"{event['title']} — {event['date']}",
                value=f"🗂️ {event['type']}\n📝 {event['description']}\n🔗 [View in Notion]({event['notion_url']})",
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Notion(bot))
