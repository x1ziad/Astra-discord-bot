import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import json
import os


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lore_file = "data/stellaris_lore.json"

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Load Stellaris lore data
        self.stellaris_lore = self.load_lore_data()

        # Stellaris empire types with emojis and descriptions
        self.empire_types = {
            "🏛️": {
                "name": "Democratic Empire",
                "description": "A beacon of freedom and equality in the galaxy",
                "ethics": "Egalitarian, Xenophile",
                "government": "Democratic",
            },
            "👑": {
                "name": "Imperial Authority",
                "description": "Rule through strength and traditional hierarchy",
                "ethics": "Authoritarian, Spiritualist",
                "government": "Imperial",
            },
            "🤖": {
                "name": "Machine Intelligence",
                "description": "Logic and efficiency above all biological concerns",
                "ethics": "Gestalt Consciousness",
                "government": "Machine Intelligence",
            },
            "🧠": {
                "name": "Hive Mind",
                "description": "Unity of thought, unity of purpose",
                "ethics": "Gestalt Consciousness",
                "government": "Hive Mind",
            },
            "⚔️": {
                "name": "Military Junta",
                "description": "Strength through conquest and military might",
                "ethics": "Militarist, Authoritarian",
                "government": "Military Junta",
            },
            "🏴‍☠️": {
                "name": "Criminal Syndicate",
                "description": "Profit through any means necessary",
                "ethics": "Criminal Heritage",
                "government": "Criminal Syndicate",
            },
            "🌟": {
                "name": "Enlightened Republic",
                "description": "Knowledge and progress guide our civilization",
                "ethics": "Materialist, Egalitarian",
                "government": "Oligarchic",
            },
            "🛡️": {
                "name": "Defensive Coalition",
                "description": "Peace through strength and preparedness",
                "ethics": "Pacifist, Xenophile",
                "government": "Democratic",
            },
            "🔬": {
                "name": "Science Directorate",
                "description": "The pursuit of knowledge above all else",
                "ethics": "Materialist, Pacifist",
                "government": "Technocracy",
            },
            "⛪": {
                "name": "Divine Empire",
                "description": "Faith guides our path among the stars",
                "ethics": "Spiritualist, Authoritarian",
                "government": "Imperial",
            },
        }

    def load_lore_data(self):
        """Load Stellaris lore from JSON file"""
        default_lore = {
            "origins": {
                "void_dwellers": "Your species has spent generations living in massive space habitats orbiting your homeworld.",
                "scion": "Your empire is the protégé of one of the Fallen Empires, granting unique advantages.",
                "lost_colony": "Your species are the descendants of a lost colony ship from another civilization.",
                "remnants": "Your homeworld bears the scars of a devastating planetary war.",
                "mechanist": "Your society has embraced robotic labor and artificial intelligence.",
                "syncretic_evolution": "Your species has evolved alongside another species on your homeworld.",
                "life_seeded": "Your species evolved on a rare Gaia world of perfect habitability.",
                "post_apocalyptic": "Your civilization survived a nuclear apocalypse and rebuilt from the ashes.",
            },
            "megastructures": {
                "dyson_sphere": "A massive structure that encloses a star to harvest its entire energy output.",
                "ring_world": "An artificial ring-shaped world that orbits a star, providing massive living space.",
                "science_nexus": "A research facility of unprecedented scale, advancing scientific knowledge.",
                "sentry_array": "A galaxy-spanning sensor network that reveals the location of all other empires.",
                "mega_art_installation": "A colossal artistic creation that inspires unity across your empire.",
                "strategic_coordination_center": "A military command hub that coordinates fleets across the galaxy.",
                "mega_shipyard": "A massive construction facility capable of building the largest ships.",
                "matter_decompressor": "A structure that breaks down planets to harvest their raw materials.",
            },
            "species_traits": {
                "adaptive": "This species is highly adaptable to different environments.",
                "intelligent": "This species has enhanced cognitive abilities.",
                "strong": "This species possesses enhanced physical strength.",
                "resilient": "This species can withstand harsh conditions better than most.",
                "natural_engineers": "This species has an innate understanding of technology and engineering.",
                "natural_physicists": "This species excels at understanding the fundamental laws of the universe.",
                "natural_sociologists": "This species has deep insights into social structures and governance.",
                "rapid_breeders": "This species reproduces faster than most.",
                "slow_breeders": "This species has a slow reproductive cycle but compensates in other ways.",
                "nomadic": "This species feels comfortable living in space habitats and ships.",
            },
            "crises": {
                "prethoryn_scourge": "An extragalactic swarm of bio-ships that devours all organic matter in their path.",
                "unbidden": "Beings from another dimension that seek to unmake reality itself.",
                "contingency": "An ancient machine intelligence that activates to purge organic life.",
                "war_in_heaven": "When two Fallen Empires awaken and wage war, smaller empires must choose sides.",
            },
        }

        try:
            with open(self.lore_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Save default lore and return it
            with open(self.lore_file, "w") as f:
                json.dump(default_lore, f, indent=2)
            return default_lore

    @commands.command(name="empire")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def empire_role_picker(self, ctx):
        """Choose your Stellaris empire type with an interactive role picker"""

        embed = discord.Embed(
            title="🌌 Choose Your Stellaris Empire Type",
            description="React with an emoji to get the corresponding empire role!\n\n"
            + "Each empire type represents different playstyles and philosophies in Stellaris.",
            color=0x6A0DAD,
            timestamp=datetime.utcnow(),
        )

        # Add fields for each empire type
        for emoji, empire_data in self.empire_types.items():
            embed.add_field(
                name=f"{emoji} {empire_data['name']}",
                value=f"*{empire_data['description']}*\n**Ethics:** {empire_data['ethics']}\n**Gov:** {empire_data['government']}",
                inline=True,
            )

        embed.add_field(
            name="🗑️ Remove Role",
            value="React with 🗑️ to remove your current empire role",
            inline=False,
        )

        embed.set_footer(
            text="💡 Tip: Use !lore <topic> to learn more about Stellaris lore",
            icon_url=ctx.author.display_avatar.url,
        )

        message = await ctx.send(embed=embed)

        # Add all reaction emojis
        emoji_list = list(self.empire_types.keys()) + ["🗑️"]
        for emoji in emoji_list:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return (
                user != self.bot.user
                and str(reaction.emoji) in emoji_list
                and reaction.message.id == message.id
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300.0, check=check
            )
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Empire Selection Timeout",
                description="The empire selection has timed out. Use `!empire` to try again.",
                color=0xFF9900,
            )
            await ctx.send(embed=timeout_embed, delete_after=10)
            return

        selected_emoji = str(reaction.emoji)
        member = ctx.guild.get_member(user.id)

        if not member:
            return

        # Handle role removal
        if selected_emoji == "🗑️":
            removed_roles = []
            for emoji, empire_data in self.empire_types.items():
                role = discord.utils.get(ctx.guild.roles, name=empire_data["name"])
                if role and role in member.roles:
                    await member.remove_roles(role)
                    removed_roles.append(role.name)

            if removed_roles:
                result_embed = discord.Embed(
                    title="🗑️ Empire Role Removed",
                    description=f"{user.mention}, your empire roles have been removed: {', '.join(removed_roles)}",
                    color=0xFF6600,
                )
            else:
                result_embed = discord.Embed(
                    title="ℹ️ No Empire Roles",
                    description=f"{user.mention}, you don't have any empire roles to remove.",
                    color=0x999999,
                )

            await ctx.send(embed=result_embed, delete_after=15)
            return

        # Handle role assignment
        if selected_emoji in self.empire_types:
            empire_data = self.empire_types[selected_emoji]
            role_name = empire_data["name"]

            # Try to find existing role or create it
            role = discord.utils.get(ctx.guild.roles, name=role_name)

            if not role:
                try:
                    # Create the role with a color based on empire type
                    role_colors = {
                        "Democratic Empire": 0x0066CC,
                        "Imperial Authority": 0x800080,
                        "Machine Intelligence": 0x888888,
                        "Hive Mind": 0x663399,
                        "Military Junta": 0xCC0000,
                        "Criminal Syndicate": 0x000000,
                        "Enlightened Republic": 0x00CC66,
                        "Defensive Coalition": 0x0099FF,
                        "Science Directorate": 0x00FFFF,
                        "Divine Empire": 0xFFCC00,
                    }

                    color = discord.Color(role_colors.get(role_name, 0x6A0DAD))
                    role = await ctx.guild.create_role(
                        name=role_name,
                        color=color,
                        mentionable=True,
                        reason=f"Stellaris empire role created by {ctx.author}",
                    )

                except discord.Forbidden:
                    error_embed = discord.Embed(
                        title="❌ Permission Error",
                        description="I don't have permission to create roles. Please ask an administrator to create the role manually.",
                        color=0xFF0000,
                    )
                    await ctx.send(embed=error_embed, delete_after=15)
                    return

            # Remove other empire roles first
            for other_emoji, other_empire_data in self.empire_types.items():
                if other_emoji != selected_emoji:
                    other_role = discord.utils.get(
                        ctx.guild.roles, name=other_empire_data["name"]
                    )
                    if other_role and other_role in member.roles:
                        await member.remove_roles(other_role)

            # Add the selected role
            if role not in member.roles:
                await member.add_roles(role)

                result_embed = discord.Embed(
                    title=f"{selected_emoji} Empire Role Assigned!",
                    description=f"Welcome to the **{empire_data['name']}**, {user.mention}!\n\n*{empire_data['description']}*",
                    color=role.color,
                )

                result_embed.add_field(
                    name="📋 Empire Details",
                    value=f"**Ethics:** {empire_data['ethics']}\n**Government:** {empire_data['government']}",
                    inline=False,
                )

                result_embed.set_footer(
                    text="May your empire prosper among the stars! ⭐"
                )

            else:
                result_embed = discord.Embed(
                    title="ℹ️ Role Already Assigned",
                    description=f"{user.mention}, you already have the **{empire_data['name']}** role!",
                    color=0x999999,
                )

            await ctx.send(embed=result_embed, delete_after=30)

    @commands.command(name="lore")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stellaris_lore(self, ctx, *, topic: str = None):
        """Get Stellaris lore information about various topics"""

        if not topic:
            # Show available categories
            embed = discord.Embed(
                title="📖 Stellaris Lore Database",
                description="Explore the rich lore of Stellaris! Use `!lore <topic>` to learn more.",
                color=0x6A0DAD,
            )

            categories = list(self.stellaris_lore.keys())
            for category in categories:
                items = list(self.stellaris_lore[category].keys())
                embed.add_field(
                    name=f"🔍 {category.replace('_', ' ').title()}",
                    value=", ".join(items[:5])
                    + (f" (+{len(items)-5} more)" if len(items) > 5 else ""),
                    inline=False,
                )

            embed.add_field(
                name="💡 Examples",
                value="`!lore dyson sphere` • `!lore prethoryn scourge` • `!lore void dwellers`",
                inline=False,
            )

            await ctx.send(embed=embed)
            return

        # Search for the topic
        topic = topic.lower().replace(" ", "_")
        found_lore = None
        found_category = None

        for category, items in self.stellaris_lore.items():
            if topic in items:
                found_lore = items[topic]
                found_category = category
                break
            # Also try partial matches
            for key in items.keys():
                if topic in key or key in topic:
                    found_lore = items[key]
                    found_category = category
                    topic = key  # Update topic to the actual key
                    break
            if found_lore:
                break

        if not found_lore:
            # Search suggestions
            all_topics = []
            for items in self.stellaris_lore.values():
                all_topics.extend(items.keys())

            suggestions = [
                t for t in all_topics if topic.replace("_", "") in t.replace("_", "")
            ][:3]

            embed = discord.Embed(
                title="❌ Lore Not Found",
                description=f"No lore found for '{topic.replace('_', ' ')}'.",
                color=0xFF0000,
            )

            if suggestions:
                embed.add_field(
                    name="💡 Did you mean?",
                    value="\n".join(
                        [f"`!lore {s.replace('_', ' ')}`" for s in suggestions]
                    ),
                    inline=False,
                )

            embed.add_field(
                name="📚 Available Topics",
                value="Use `!lore` to see all available categories and topics.",
                inline=False,
            )

            await ctx.send(embed=embed, delete_after=15)
            return

        # Display the lore
        embed = discord.Embed(
            title=f"📖 {topic.replace('_', ' ').title()}",
            description=found_lore,
            color=0x6A0DAD,
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📂 Category",
            value=found_category.replace("_", " ").title(),
            inline=True,
        )

        # Add related topics from the same category
        related_topics = list(self.stellaris_lore[found_category].keys())
        if len(related_topics) > 1:
            related = [t for t in related_topics if t != topic][:3]
            if related:
                embed.add_field(
                    name="🔗 Related Topics",
                    value=", ".join([t.replace("_", " ").title() for t in related]),
                    inline=True,
                )

        embed.set_footer(
            text="🌌 Knowledge is power in the galaxy",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="rolecount")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def empire_role_count(self, ctx):
        """Show the count of members with each Stellaris empire role"""

        embed = discord.Embed(
            title="📊 Stellaris Empire Census",
            description="Current distribution of empire roles in this server",
            color=0x6A0DAD,
            timestamp=datetime.utcnow(),
        )

        total_members = 0
        role_data = []

        for emoji, empire_data in self.empire_types.items():
            role = discord.utils.get(ctx.guild.roles, name=empire_data["name"])
            count = len(role.members) if role else 0
            total_members += count

            if count > 0:
                role_data.append((emoji, empire_data["name"], count))

        # Sort by member count
        role_data.sort(key=lambda x: x[2], reverse=True)

        if role_data:
            census_text = ""
            for emoji, name, count in role_data:
                percentage = (count / total_members * 100) if total_members > 0 else 0
                census_text += (
                    f"{emoji} **{name}**: {count} members ({percentage:.1f}%)\n"
                )

            embed.add_field(
                name="🏛️ Empire Distribution", value=census_text, inline=False
            )

            embed.add_field(
                name="📈 Summary",
                value=f"**Total Empire Members:** {total_members}\n**Most Popular:** {role_data[0][1] if role_data else 'None'}",
                inline=True,
            )
        else:
            embed.add_field(
                name="🌌 No Empires Yet",
                value="No members have chosen empire roles yet! Use `!empire` to get started.",
                inline=False,
            )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)

    @commands.command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def add_custom_role(self, ctx, role_name: str, emoji: str = None):
        """Add a custom empire role (Admin only)"""

        # Check if role already exists
        existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
        if existing_role:
            embed = discord.Embed(
                title="❌ Role Already Exists",
                description=f"A role named '{role_name}' already exists in this server.",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        try:
            # Create the role
            role = await ctx.guild.create_role(
                name=role_name,
                color=discord.Color.random(),
                mentionable=True,
                reason=f"Custom empire role created by {ctx.author}",
            )

            embed = discord.Embed(
                title="✅ Role Created",
                description=f"Successfully created the **{role_name}** role!",
                color=0x00FF00,
            )

            embed.add_field(
                name="🎨 Role Details",
                value=f"**Name:** {role.name}\n**Color:** {role.color}\n**Mentionable:** Yes",
                inline=True,
            )

            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to create roles.",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=10)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to create role: {str(e)}",
                color=0xFF0000,
            )
            await ctx.send(embed=embed, delete_after=10)


async def setup(bot):
    await bot.add_cog(Roles(bot))
