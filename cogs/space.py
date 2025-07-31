"""
Space-related commands and features for Astra
Includes NASA APOD, space facts, and astronomy information
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random
from datetime import datetime, timedelta
import asyncio
import json
from typing import Optional, List
from pathlib import Path
import os

from config.enhanced_config import config_manager, feature_enabled, channel_only
from logger.logger import log_performance
from ui.ui_components import PaginatedView


class Space(commands.GroupCog, name="space"):
    """Space exploration and astronomy commands"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

        # Cache directory
        self.cache_dir = Path("data/space")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Get NASA API key from environment or use demo key
        self.nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

        # Load space facts
        self.space_facts = self._load_space_facts()

        # Track API rate limits
        self.last_api_call = datetime.min

        self.logger.info(f"Space cog initialized with {len(self.space_facts)} facts")

    def _load_space_facts(self) -> List[str]:
        """Load space facts from base data and custom data file"""
        # Base space facts
        base_facts = [
            "A day on Venus is longer than its year - Venus rotates very slowly!",
            "There are more stars in the universe than grains of sand on all the beaches on Earth.",
            "Neutron stars are so dense that a teaspoon of their material would weigh about 6 billion tons.",
            "The Milky Way galaxy is on a collision course with Andromeda, but don't worry - it won't happen for 4.5 billion years!",
            "Jupiter's Great Red Spot is a storm that has been raging for at least 400 years.",
            "Saturn's density is so low that it would float if you could find a bathtub big enough!",
            "One million Earths could fit inside the Sun, but the Sun is actually a pretty average-sized star.",
            "The footprints left by Apollo astronauts on the Moon will probably still be there in 100 million years.",
            "There's a planet where it rains glass sideways - HD 189733b experiences winds of 4,300 mph!",
            "The ISS travels at 17,500 mph and orbits Earth every 90 minutes.",
            "Proxima Centauri, our nearest star neighbor, would take 73,000 years to reach with current technology.",
            "The observable universe is about 93 billion light-years in diameter.",
            "Black holes don't actually suck - they're just incredibly massive and bend spacetime.",
            "Olympus Mons on Mars is the largest volcano in our solar system - it's 3 times taller than Mount Everest!",
            "A year on Pluto lasts 248 Earth years - it hasn't completed one orbit since its discovery in 1930!",
        ]

        # Try to load additional facts from file
        try:
            facts_file = self.cache_dir / "space_facts.json"
            if facts_file.exists():
                with open(facts_file, "r") as f:
                    additional_facts = json.load(f)
                    if isinstance(additional_facts, list):
                        base_facts.extend(additional_facts)
                        self.logger.info(
                            f"Loaded {len(additional_facts)} additional space facts"
                        )
        except Exception as e:
            self.logger.error(f"Error loading space facts: {e}")

        return base_facts

    @app_commands.command(
        name="apod", description="Get NASA's Astronomy Picture of the Day"
    )
    @app_commands.describe(date="Optional specific date (YYYY-MM-DD)")
    @app_commands.checks.cooldown(1, 30)  # 30 second cooldown
    @feature_enabled("space_content")
    async def apod_command(
        self, interaction: discord.Interaction, date: Optional[str] = None
    ):
        """Fetch NASA's Astronomy Picture of the Day"""
        await interaction.response.defer()  # Defer response since API call might take time

        try:
            # Validate date format if provided
            parsed_date = None
            if date:
                try:
                    parsed_date = datetime.strptime(date, "%Y-%m-%d")
                    # Check if date is valid (not in future and not before APOD started)
                    if parsed_date > datetime.now():
                        await interaction.followup.send(
                            "❌ The date cannot be in the future.", ephemeral=True
                        )
                        return
                    if parsed_date < datetime(
                        1995, 6, 16
                    ):  # APOD started on June 16, 1995
                        await interaction.followup.send(
                            "❌ APOD began on June 16, 1995. Please choose a date after that.",
                            ephemeral=True,
                        )
                        return
                    date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    await interaction.followup.send(
                        "❌ Invalid date format. Please use YYYY-MM-DD.", ephemeral=True
                    )
                    return

            # Check rate limit
            now = datetime.now()
            if (
                now - self.last_api_call
            ).total_seconds() < 1.0:  # Minimum 1 second between calls
                await asyncio.sleep(1)  # Wait to avoid hitting rate limit

            self.last_api_call = now

            # Check cache first if we're requesting today's APOD
            if not date:
                cache_file = (
                    self.cache_dir
                    / f"apod_cache_{datetime.now().strftime('%Y-%m-%d')}.json"
                )
                if cache_file.exists():
                    try:
                        with open(cache_file, "r") as f:
                            data = json.load(f)
                        self.logger.info("Using cached APOD data")
                        await self._send_apod_embed(interaction, data)
                        return
                    except Exception as e:
                        self.logger.error(f"Error reading APOD cache: {e}")
                        # Continue to API call if cache read fails

            # Make API request
            async with aiohttp.ClientSession() as session:
                params = {"api_key": self.nasa_api_key}
                if date:
                    params["date"] = date

                url = "https://api.nasa.gov/planetary/apod"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Cache today's APOD
                        if not date:
                            try:
                                with open(cache_file, "w") as f:
                                    json.dump(data, f)
                            except Exception as e:
                                self.logger.error(f"Error caching APOD: {e}")

                        await self._send_apod_embed(interaction, data)
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"NASA API error: {response.status} - {error_text}"
                        )
                        raise Exception(f"NASA API returned status {response.status}")

        except Exception as e:
            self.logger.error(f"APOD command error: {str(e)}")
            error_embed = discord.Embed(
                title="❌ APOD Error",
                description="Sorry, couldn't fetch the astronomy picture. The NASA API might be temporarily unavailable.",
                color=self.config.get_color("error"),
            )
            await interaction.followup.send(embed=error_embed)

    async def _send_apod_embed(self, interaction: discord.Interaction, data: dict):
        """Format and send APOD data as embed"""
        embed = discord.Embed(
            title=f"🌌 {data['title']}",
            description=(
                data.get("explanation", "No description available")[:2000] + "..."
                if len(data.get("explanation", "")) > 2000
                else data.get("explanation", "No description available")
            ),
            color=self.config.get_color("space"),
        )

        # Add date information
        if "date" in data:
            try:
                apod_date = datetime.strptime(data["date"], "%Y-%m-%d")
                embed.timestamp = apod_date
                embed.set_footer(
                    text="NASA Astronomy Picture of the Day",
                    icon_url="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png",
                )
            except ValueError:
                embed.set_footer(text=f"NASA APOD - {data['date']}")

        # Add image or video
        if data.get("media_type") == "image":
            # Use high-resolution image if available
            image_url = data.get("hdurl", data.get("url"))
            embed.set_image(url=image_url)

            # Add credit information
            if "copyright" in data:
                embed.add_field(name="📸 Credit", value=data["copyright"], inline=True)
        elif data.get("media_type") == "video":
            embed.add_field(
                name="🎥 Video",
                value=f"[Watch Here]({data['url']})",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="fact", description="Get a random space fact")
    @app_commands.describe(category="Fact category (optional)")
    @app_commands.checks.cooldown(1, 5)  # 5 second cooldown
    @feature_enabled("space_content")
    async def fact_command(
        self, interaction: discord.Interaction, category: Optional[str] = None
    ):
        """Get a random space fact"""
        fact = random.choice(self.space_facts)

        embed = discord.Embed(
            title="🚀 Space Fact",
            description=fact,
            color=self.config.get_color("space"),
        )

        embed.set_footer(
            text=f"Astra has {len(self.space_facts)} space facts in its database"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="meteor", description="Get information about upcoming meteor showers"
    )
    @app_commands.checks.cooldown(1, 30)  # 30 second cooldown
    @feature_enabled("space_content")
    async def meteor_command(self, interaction: discord.Interaction):
        """Get information about upcoming meteor showers"""
        current_month = datetime.now().month

        # Meteor shower calendar
        meteor_showers = {
            1: {
                "name": "Quadrantids",
                "peak": "January 3-4",
                "rate": "60-200 meteors/hour",
                "parent": "2003 EH1 (extinct comet)",
                "notes": "One of the best annual meteor showers, with bright meteors and occasional fireballs",
            },
            2: {
                "name": "α-Centaurids",
                "peak": "February 8",
                "rate": "6 meteors/hour",
                "parent": "Unknown",
                "notes": "Visible from southern hemisphere, bright meteors with persistent trains",
            },
            3: {
                "name": "γ-Normids",
                "peak": "March 14",
                "rate": "6 meteors/hour",
                "parent": "Unknown",
                "notes": "A minor shower, but visible during dark nights with good conditions",
            },
            4: {
                "name": "Lyrids",
                "peak": "April 21-22",
                "rate": "15-20 meteors/hour",
                "parent": "Comet Thatcher",
                "notes": "One of the oldest known meteor showers, observed for over 2,700 years",
            },
            5: {
                "name": "η-Aquariids",
                "peak": "May 5-6",
                "rate": "30-60 meteors/hour",
                "parent": "Halley's Comet",
                "notes": "Best viewed from the southern hemisphere before dawn",
            },
            6: {
                "name": "Arietids",
                "peak": "June 7",
                "rate": "30 meteors/hour",
                "parent": "Marsden and Kracht comet groups",
                "notes": "One of the most intense daylight meteor showers, best detected by radio",
            },
            7: {
                "name": "δ-Aquariids",
                "peak": "July 28-29",
                "rate": "15-20 meteors/hour",
                "parent": "Comet 96P/Machholz",
                "notes": "Better viewed from southern latitudes, with good rates for a week",
            },
            8: {
                "name": "Perseids",
                "peak": "August 11-13",
                "rate": "50-100 meteors/hour",
                "parent": "Comet Swift-Tuttle",
                "notes": "One of the most popular meteor showers with bright, fast meteors and fireballs",
            },
            9: {
                "name": "Draconids",
                "peak": "October 8-9",
                "rate": "5-10 meteors/hour",
                "parent": "Comet 21P/Giacobini-Zinner",
                "notes": "Variable rates; occasionally produces meteor storms (thousands/hour)",
            },
            10: {
                "name": "Orionids",
                "peak": "October 20-21",
                "rate": "15-20 meteors/hour",
                "parent": "Halley's Comet",
                "notes": "Fast meteors with fine trains, sometimes leaving persistent trails",
            },
            11: {
                "name": "Leonids",
                "peak": "November 17-18",
                "rate": "10-15 meteors/hour",
                "parent": "Comet Tempel-Tuttle",
                "notes": "Produces meteor storms every 33 years, with the next one due in the 2030s",
            },
            12: {
                "name": "Geminids",
                "peak": "December 13-14",
                "rate": "120-150 meteors/hour",
                "parent": "Asteroid 3200 Phaethon",
                "notes": "One of the most consistent and spectacular annual meteor showers",
            },
        }

        # Get data for current, next, and upcoming months
        current_shower = meteor_showers.get(current_month)
        next_month = current_month + 1 if current_month < 12 else 1
        next_shower = meteor_showers.get(next_month)

        # Determine months to show
        months_to_show = [current_month]
        if current_month != next_month:
            months_to_show.append(next_month)

        # Create embed
        embed = discord.Embed(
            title="☄️ Meteor Shower Information",
            description="Here are the details about current and upcoming meteor showers.",
            color=self.config.get_color("space"),
        )

        # Add fields for each shower
        for month in months_to_show:
            shower = meteor_showers.get(month)
            if shower:
                # Format the name with timing indicator
                name_prefix = "🔭 " if month == current_month else "🗓️ "
                time_indicator = (
                    "This Month" if month == current_month else "Next Month"
                )

                embed.add_field(
                    name=f"{name_prefix}{shower['name']} ({time_indicator})",
                    value=f"**Peak:** {shower['peak']}\n"
                    f"**Rate:** {shower['rate']}\n"
                    f"**Parent Body:** {shower['parent']}\n"
                    f"**Notes:** {shower['notes']}",
                    inline=False,
                )

        # Add viewing tips
        embed.add_field(
            name="🔭 Viewing Tips",
            value="• Find a dark location away from city lights\n"
            "• Allow 20-30 minutes for your eyes to adjust to darkness\n"
            "• Look up at the whole sky, not just at the radiant point\n"
            "• Use a reclining chair for comfortable viewing\n"
            "• No telescope needed - use your naked eyes for the widest view",
            inline=False,
        )

        embed.set_footer(text="Data from International Meteor Organization")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="iss", description="Track the International Space Station"
    )
    @app_commands.checks.cooldown(1, 30)  # 30 second cooldown
    @feature_enabled("space_content.iss_tracking")
    async def iss_command(self, interaction: discord.Interaction):
        """Get current ISS location and information"""
        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                # Get ISS current location
                async with session.get(
                    "http://api.open-notify.org/iss-now.json"
                ) as response:
                    if response.status == 200:
                        location_data = await response.json()

                        # Get ISS crew
                        crew_data = {"people": []}
                        try:
                            async with session.get(
                                "http://api.open-notify.org/astros.json"
                            ) as crew_response:
                                if crew_response.status == 200:
                                    crew_data = await crew_response.json()
                        except Exception as e:
                            self.logger.error(f"Error fetching ISS crew data: {e}")

                        # Create embed
                        embed = discord.Embed(
                            title="🛰️ International Space Station",
                            description="Real-time tracking information for the ISS",
                            color=self.config.get_color("space"),
                            timestamp=datetime.utcnow(),
                        )

                        # Location information
                        lat = float(location_data["iss_position"]["latitude"])
                        lon = float(location_data["iss_position"]["longitude"])

                        embed.add_field(
                            name="📍 Current Position",
                            value=f"**Latitude:** {lat:.4f}°\n**Longitude:** {lon:.4f}°",
                            inline=True,
                        )

                        embed.add_field(
                            name="🌍 Map View",
                            value=f"[View on Map](https://www.google.com/maps/@{lat},{lon},4z/data=!3m1!1e3)",
                            inline=True,
                        )

                        # ISS Crew information
                        iss_crew = []
                        for person in crew_data.get("people", []):
                            if person.get("craft") == "ISS":
                                iss_crew.append(person.get("name"))

                        if iss_crew:
                            embed.add_field(
                                name=f"👨‍🚀 Current Crew ({len(iss_crew)})",
                                value=(
                                    "\n".join(iss_crew)
                                    if len(iss_crew) < 10
                                    else "\n".join(iss_crew[:9])
                                    + f"\n...and {len(iss_crew) - 9} more"
                                ),
                                inline=False,
                            )

                        # ISS Facts
                        embed.add_field(
                            name="ℹ️ Station Facts",
                            value="• Orbits Earth every ~90 minutes\n"
                            "• Travels at 28,000 km/h (17,500 mph)\n"
                            "• Altitude: ~408 km (254 miles)\n"
                            "• Mass: 420,000 kg (925,000 lbs)\n"
                            "• Length: 109 meters (356 feet)",
                            inline=False,
                        )

                        # Set thumbnail
                        embed.set_thumbnail(
                            url="https://upload.wikimedia.org/wikipedia/commons/0/04/International_Space_Station_after_undocking_of_STS-132.jpg"
                        )
                        embed.set_footer(
                            text="Data from Open Notify API • ISS position updates every 5 seconds"
                        )

                        await interaction.followup.send(embed=embed)
                    else:
                        raise Exception(f"API returned status {response.status}")
        except Exception as e:
            self.logger.error(f"Error in ISS tracking command: {e}")
            error_embed = discord.Embed(
                title="❌ ISS Tracking Error",
                description="Sorry, couldn't fetch ISS location data right now.",
                color=self.config.get_color("error"),
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(
        name="launch", description="Get information about upcoming space launches"
    )
    @app_commands.checks.cooldown(1, 60)  # 60 second cooldown
    @feature_enabled("space_content.launch_notifications")
    async def launch_command(self, interaction: discord.Interaction):
        """Get information about upcoming space launches"""
        # This would ideally use a real API like SpaceX API or Launch Library
        # For now, we'll create a simple embed with general info

        embed = discord.Embed(
            title="🚀 Upcoming Space Launches",
            description="Information about upcoming space missions",
            color=self.config.get_color("space"),
            timestamp=datetime.utcnow(),
        )

        # Launch tracking services
        embed.add_field(
            name="📱 Launch Tracking Services",
            value="• [Next Spaceflight](https://nextspaceflight.com/)\n"
            "• [Space Launch Now](https://spacelaunchnow.me/)\n"
            "• [Space Launch Schedule](https://www.spacelaunchschedule.com/)",
            inline=False,
        )

        # Agency websites
        embed.add_field(
            name="🏢 Space Agency Websites",
            value="• [NASA](https://www.nasa.gov/launchschedule/)\n"
            "• [SpaceX](https://www.spacex.com/launches/)\n"
            "• [ESA](https://www.esa.int/Enabling_Support/Space_Transportation/Launch_schedule)\n"
            "• [Rocket Lab](https://www.rocketlabusa.com/missions/)",
            inline=False,
        )

        # Live streams
        embed.add_field(
            name="📺 Live Stream Channels",
            value="• [NASA TV](https://www.nasa.gov/nasalive)\n"
            "• [SpaceX YouTube](https://www.youtube.com/spacex)\n"
            "• [Everyday Astronaut](https://www.youtube.com/c/EverydayAstronaut)\n"
            "• [NASASpaceflight](https://www.youtube.com/c/NASASpaceflight)",
            inline=False,
        )

        embed.set_footer(text="Use the /subscribe command to get launch notifications")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="planets", description="Information about planets in our solar system"
    )
    @app_commands.describe(planet="Select a specific planet to view details")
    @app_commands.checks.cooldown(1, 15)
    @feature_enabled("space_content")
    async def planets_command(
        self, interaction: discord.Interaction, planet: Optional[str] = None
    ):
        """Get information about planets in our solar system"""
        planets = {
            "mercury": {
                "name": "Mercury",
                "emoji": "☿️",
                "description": "The smallest planet in our solar system and closest to the Sun.",
                "diameter": "4,879 km",
                "distance_from_sun": "57.9 million km",
                "day_length": "59 Earth days",
                "year_length": "88 Earth days",
                "temperature": "-173°C to 427°C",
                "moons": 0,
                "interesting_fact": "Despite being closest to the Sun, Mercury is not the hottest planet - that's Venus.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Mercury_in_color_-_Prockter07-edit1.jpg/600px-Mercury_in_color_-_Prockter07-edit1.jpg",
            },
            "venus": {
                "name": "Venus",
                "emoji": "♀️",
                "description": "Similar in size to Earth but with a toxic atmosphere and extreme temperatures.",
                "diameter": "12,104 km",
                "distance_from_sun": "108.2 million km",
                "day_length": "243 Earth days",
                "year_length": "225 Earth days",
                "temperature": "462°C",
                "moons": 0,
                "interesting_fact": "Venus rotates backwards compared to other planets, and a day on Venus is longer than its year.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Venus-real_color.jpg",
            },
            "earth": {
                "name": "Earth",
                "emoji": "🌎",
                "description": "Our home planet and the only known celestial body to harbor life.",
                "diameter": "12,742 km",
                "distance_from_sun": "149.6 million km",
                "day_length": "24 hours",
                "year_length": "365.25 days",
                "temperature": "-88°C to 58°C",
                "moons": 1,
                "interesting_fact": "Earth's atmosphere is 78% nitrogen, 21% oxygen, and 1% other gases including CO₂.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/The_Blue_Marble_%28remastered%29.jpg/600px-The_Blue_Marble_%28remastered%29.jpg",
            },
            "mars": {
                "name": "Mars",
                "emoji": "♂️",
                "description": "The red planet, named after the Roman god of war.",
                "diameter": "6,779 km",
                "distance_from_sun": "227.9 million km",
                "day_length": "24.6 hours",
                "year_length": "687 Earth days",
                "temperature": "-153°C to 20°C",
                "moons": 2,
                "interesting_fact": "Mars has the largest volcano in the solar system, Olympus Mons, standing at 25 km tall.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/600px-OSIRIS_Mars_true_color.jpg",
            },
            "jupiter": {
                "name": "Jupiter",
                "emoji": "♃",
                "description": "The largest planet in our solar system, a gas giant with a distinctive Great Red Spot.",
                "diameter": "139,820 km",
                "distance_from_sun": "778.5 million km",
                "day_length": "9.9 hours",
                "year_length": "11.9 Earth years",
                "temperature": "-145°C",
                "moons": 79,
                "interesting_fact": "Jupiter's Great Red Spot is a storm that has been raging for at least 400 years.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/600px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg",
            },
            "saturn": {
                "name": "Saturn",
                "emoji": "♄",
                "description": "Known for its spectacular ring system, this gas giant is the second largest planet.",
                "diameter": "116,460 km",
                "distance_from_sun": "1.4 billion km",
                "day_length": "10.7 hours",
                "year_length": "29.5 Earth years",
                "temperature": "-178°C",
                "moons": 82,
                "interesting_fact": "Saturn has a density lower than water, which means it would float if placed in a giant bathtub.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/600px-Saturn_during_Equinox.jpg",
            },
            "uranus": {
                "name": "Uranus",
                "emoji": "⛢",
                "description": "The tilted ice giant that rotates on its side, with a blue-green color.",
                "diameter": "50,724 km",
                "distance_from_sun": "2.9 billion km",
                "day_length": "17.2 hours",
                "year_length": "84 Earth years",
                "temperature": "-224°C",
                "moons": 27,
                "interesting_fact": "Uranus rotates on its side with an axial tilt of about 98 degrees, likely caused by a massive collision.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Uranus2.jpg/600px-Uranus2.jpg",
            },
            "neptune": {
                "name": "Neptune",
                "emoji": "♆",
                "description": "The windiest planet, this distant ice giant has the strongest winds in the solar system.",
                "diameter": "49,244 km",
                "distance_from_sun": "4.5 billion km",
                "day_length": "16.1 hours",
                "year_length": "165 Earth years",
                "temperature": "-218°C",
                "moons": 14,
                "interesting_fact": "Neptune was predicted mathematically before it was observed directly, based on Uranus's orbit.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/600px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg",
            },
            "pluto": {
                "name": "Pluto (Dwarf Planet)",
                "emoji": "♇",
                "description": "A dwarf planet in the Kuiper Belt, demoted from planet status in 2006.",
                "diameter": "2,377 km",
                "distance_from_sun": "5.9 billion km (average)",
                "day_length": "6.4 Earth days",
                "year_length": "248 Earth years",
                "temperature": "-229°C",
                "moons": 5,
                "interesting_fact": "Pluto has a heart-shaped glacier called Tombaugh Regio, visible in images from the New Horizons mission.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Pluto_in_True_Color_-_High-Res.jpg/600px-Pluto_in_True_Color_-_High-Res.jpg",
            },
        }

        # If planet is specified, show details about that planet
        if planet and planet.lower() in planets:
            planet_data = planets[planet.lower()]

            embed = discord.Embed(
                title=f"{planet_data['emoji']} {planet_data['name']}",
                description=planet_data["description"],
                color=self.config.get_color("space"),
            )

            # Add basic facts
            embed.add_field(
                name="📊 Basic Facts",
                value=f"**Diameter:** {planet_data['diameter']}\n"
                f"**Distance from Sun:** {planet_data['distance_from_sun']}\n"
                f"**Day Length:** {planet_data['day_length']}\n"
                f"**Year Length:** {planet_data['year_length']}\n"
                f"**Temperature:** {planet_data['temperature']}\n"
                f"**Moons:** {planet_data['moons']}",
                inline=False,
            )

            # Add interesting fact
            embed.add_field(
                name="⭐ Did You Know?",
                value=planet_data["interesting_fact"],
                inline=False,
            )

            # Set planet image
            embed.set_image(url=planet_data["image"])

            await interaction.response.send_message(embed=embed)
            return

        # If no planet specified or invalid planet, show overview of all planets
        embeds = []

        # Main overview embed
        overview_embed = discord.Embed(
            title="🪐 Our Solar System",
            description="Select a specific planet with `/planets [name]` for detailed information.",
            color=self.config.get_color("space"),
        )

        # Group inner, outer and dwarf planets
        inner_planets = "**Inner Planets:**\n" + "\n".join(
            [
                f"{planets['mercury']['emoji']} Mercury",
                f"{planets['venus']['emoji']} Venus",
                f"{planets['earth']['emoji']} Earth",
                f"{planets['mars']['emoji']} Mars",
            ]
        )

        outer_planets = "**Outer Planets:**\n" + "\n".join(
            [
                f"{planets['jupiter']['emoji']} Jupiter",
                f"{planets['saturn']['emoji']} Saturn",
                f"{planets['uranus']['emoji']} Uranus",
                f"{planets['neptune']['emoji']} Neptune",
            ]
        )

        dwarf_planets = "**Dwarf Planets:**\n" + f"{planets['pluto']['emoji']} Pluto"

        overview_embed.add_field(
            name="☀️ Inner Solar System", value=inner_planets, inline=True
        )
        overview_embed.add_field(
            name="🌌 Outer Solar System", value=outer_planets, inline=True
        )
        overview_embed.add_field(name="💫 Beyond", value=dwarf_planets, inline=True)

        # Add solar system image
        overview_embed.set_image(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Planets2013.svg/1280px-Planets2013.svg.png"
        )

        # Add instructions for detailed views
        overview_embed.add_field(
            name="💡 Pro Tip",
            value="Use `/planets mercury` to view details about Mercury\n"
            "Available planets: mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto",
            inline=False,
        )

        await interaction.response.send_message(embed=overview_embed)


async def setup(bot):
    await bot.add_cog(Space(bot))
