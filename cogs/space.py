import discord
from discord.ext import commands
import aiohttp
import random
from datetime import datetime
import asyncio


class Space(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Space facts database
        self.space_facts = [
            "A day on Venus is longer than its year - Venus rotates very slowly!",
            "There are more possible games of chess than atoms in the observable universe.",
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

    @commands.command(name="apod")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def astronomy_picture_of_the_day(self, ctx):
        """Fetch NASA's Astronomy Picture of the Day"""
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    # NASA APOD API (no key required for basic usage)
                    url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()

                            embed = discord.Embed(
                                title=f"🌌 {data['title']}",
                                description=(
                                    data.get("explanation", "No description available")[
                                        :2000
                                    ]
                                    + "..."
                                    if len(data.get("explanation", "")) > 2000
                                    else data.get(
                                        "explanation", "No description available"
                                    )
                                ),
                                color=0x1E1F23,
                                timestamp=datetime.strptime(data["date"], "%Y-%m-%d"),
                            )

                            if data.get("media_type") == "image":
                                embed.set_image(url=data["url"])
                            elif data.get("media_type") == "video":
                                embed.add_field(
                                    name="🎥 Video Link",
                                    value=f"[Watch Here]({data['url']})",
                                    inline=False,
                                )

                            embed.set_footer(
                                text="NASA Astronomy Picture of the Day",
                                icon_url="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png",
                            )

                            await ctx.send(embed=embed)
                        else:
                            raise Exception(
                                f"NASA API returned status {response.status}"
                            )

            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ APOD Error",
                    description="Sorry, couldn't fetch today's astronomy picture. The NASA API might be temporarily unavailable.",
                    color=0xFF0000,
                )
                await ctx.send(embed=error_embed)

    @commands.command(name="fact")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def random_space_fact(self, ctx):
        """Get a random space fact"""
        fact = random.choice(self.space_facts)

        embed = discord.Embed(title="🚀 Space Fact", description=fact, color=0x9932CC)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/123456789/123456789/space_icon.png"
        )  # Replace with your space icon

        await ctx.send(embed=embed)

    @commands.command(name="meteor")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def meteor_showers(self, ctx):
        """Get information about upcoming meteor showers"""
        current_month = datetime.now().month

        # Meteor shower calendar
        meteor_showers = {
            1: {
                "name": "Quadrantids",
                "peak": "January 3-4",
                "rate": "60-200 meteors/hour",
            },
            2: {"name": "α-Centaurids", "peak": "February 8", "rate": "6 meteors/hour"},
            3: {"name": "γ-Normids", "peak": "March 14", "rate": "6 meteors/hour"},
            4: {"name": "Lyrids", "peak": "April 21-22", "rate": "15-20 meteors/hour"},
            5: {"name": "η-Aquariids", "peak": "May 5-6", "rate": "30-60 meteors/hour"},
            6: {"name": "Arietids", "peak": "June 7", "rate": "30 meteors/hour"},
            7: {
                "name": "δ-Aquariids",
                "peak": "July 28-29",
                "rate": "15-20 meteors/hour",
            },
            8: {
                "name": "Perseids",
                "peak": "August 11-12",
                "rate": "50-100 meteors/hour",
            },
            9: {
                "name": "Draconids",
                "peak": "October 8-9",
                "rate": "5-10 meteors/hour",
            },
            10: {
                "name": "Orionids",
                "peak": "October 20-21",
                "rate": "15-75 meteors/hour",
            },
            11: {
                "name": "Leonids",
                "peak": "November 17-18",
                "rate": "10-15 meteors/hour",
            },
            12: {
                "name": "Geminids",
                "peak": "December 13-14",
                "rate": "60-120 meteors/hour",
            },
        }

        current_shower = meteor_showers.get(current_month)

        embed = discord.Embed(title="☄️ Meteor Shower Information", color=0xFFD700)

        if current_shower:
            embed.add_field(
                name=f"This Month: {current_shower['name']}",
                value=f"**Peak:** {current_shower['peak']}\n**Rate:** {current_shower['rate']}",
                inline=False,
            )

        # Show next month too
        next_month = current_month + 1 if current_month < 12 else 1
        next_shower = meteor_showers.get(next_month)

        if next_shower:
            embed.add_field(
                name=f"Next Month: {next_shower['name']}",
                value=f"**Peak:** {next_shower['peak']}\n**Rate:** {next_shower['rate']}",
                inline=False,
            )

        embed.add_field(
            name="🔭 Viewing Tips",
            value="• Find a dark location away from city lights\n• Look up after midnight\n• Allow 20-30 minutes for your eyes to adjust\n• No telescope needed - use your naked eyes!",
            inline=False,
        )

        embed.set_footer(text="Data from International Meteor Organization")

        await ctx.send(embed=embed)

    @commands.command(name="iss")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def iss_location(self, ctx):
        """Get current ISS location and next pass times"""
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    # Get ISS current location
                    async with session.get(
                        "http://api.open-notify.org/iss-now.json"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()

                            embed = discord.Embed(
                                title="🛰️ International Space Station",
                                description="Current location and status",
                                color=0x0099FF,
                                timestamp=datetime.utcnow(),
                            )

                            lat = float(data["iss_position"]["latitude"])
                            lon = float(data["iss_position"]["longitude"])

                            embed.add_field(
                                name="📍 Current Position",
                                value=f"**Latitude:** {lat:.2f}°\n**Longitude:** {lon:.2f}°",
                                inline=True,
                            )

                            embed.add_field(
                                name="🌍 Map View",
                                value=f"[View on Map](https://www.google.com/maps/@{lat},{lon},4z)",
                                inline=True,
                            )

                            embed.add_field(
                                name="ℹ️ Fun Facts",
                                value="• Orbits Earth every ~90 minutes\n• Travels at 17,500 mph\n• Altitude: ~408 km (254 miles)",
                                inline=False,
                            )

                            embed.set_footer(text="Data from Open Notify API")

                            await ctx.send(embed=embed)
                        else:
                            raise Exception("API unavailable")

            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ ISS Tracking Error",
                    description="Sorry, couldn't fetch ISS location data right now.",
                    color=0xFF0000,
                )
                await ctx.send(embed=error_embed)

    @commands.command(name="launch")
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def next_launches(self, ctx):
        """Get information about upcoming space launches"""
        # This would ideally use a real API like SpaceX API or Launch Library
        # For now, we'll create a simple embed with general info

        embed = discord.Embed(
            title="🚀 Upcoming Space Launches",
            description="Keep track of humanity's journey to the stars!",
            color=0xFF6600,
        )

        embed.add_field(
            name="🔗 Resources",
            value="• [SpaceX Launches](https://www.spacex.com/launches/)\n• [NASA Launch Schedule](https://www.nasa.gov/launchschedule/)\n• [Next Spaceflight](https://nextspaceflight.com/)",
            inline=False,
        )

        embed.add_field(
            name="📱 Apps & Notifications",
            value="Consider downloading apps like 'Space Launch Now' for real-time notifications!",
            inline=False,
        )

        embed.set_footer(text="Stay tuned for live launch tracking integration!")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Space(bot))
