"""
Stellaris empire roles system for Astra Bot
Allows users to select empire roles and get lore information
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Union
from pathlib import Path

from config.unified_config import unified_config
from ui.ui_components import EmpireRoleView, HomeworldSelectView


class Roles(commands.GroupCog, name="empire"):
    """Stellaris empire role and lore commands"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # Data directory
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.lore_file = self.data_dir / "stellaris_lore.json"

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

        self.logger.info(
            f"Roles cog initialized with {len(self.empire_types)} empire types"
        )

    def load_lore_data(self) -> Dict[str, Dict[str, str]]:
        """Load Stellaris lore from JSON file or create default"""
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
            if self.lore_file.exists():
                with open(self.lore_file, "r") as f:
                    return json.load(f)

            # If file doesn't exist, create it with default data
            with open(self.lore_file, "w") as f:
                json.dump(default_lore, f, indent=2)

            return default_lore
        except Exception as e:
            self.logger.error(f"Error loading lore data: {e}")
            return default_lore

    @app_commands.command(
        name="choose", description="Choose your Stellaris empire type"
    )
    # @feature_enabled("stellaris_features.empire_roles")
    async def empire_role_command(self, interaction: discord.Interaction):
        """Choose your Stellaris empire type from a selection of options"""
        # Create the empire role selection view
        view = EmpireRoleView(self.empire_types)

        embed = discord.Embed(
            title="🌌 Choose Your Stellaris Empire Type",
            description="Select your empire from the dropdown menu below!\n\n"
            + "Each empire type represents different playstyles and philosophies in Stellaris.",
            color=self.config.get_color("stellaris"),
            timestamp=datetime.now(timezone.utc),
        )

        # Add brief descriptions of each empire type
        empires_text = ""
        for emoji, empire in self.empire_types.items():
            empires_text += f"{emoji} **{empire['name']}**: {empire['description']}\n"

        embed.add_field(name="Available Empires", value=empires_text, inline=False)

        embed.set_footer(
            text="💡 Tip: Use /empire lore to learn more about Stellaris lore",
        )

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="lore", description="Get Stellaris lore information")
    @app_commands.describe(topic="Lore topic to look up")
    @app_commands.checks.cooldown(1, 10)
    # @feature_enabled("stellaris_features.lore_system")
    async def lore_command(
        self, interaction: discord.Interaction, topic: Optional[str] = None
    ):
        """Get information about Stellaris lore topics"""
        if not topic:
            # Show available categories
            embed = discord.Embed(
                title="📖 Stellaris Lore Database",
                description="Explore the rich lore of Stellaris! Specify a topic to learn more.",
                color=self.config.get_color("stellaris"),
            )

            categories = list(self.stellaris_lore.keys())
            for category in categories:
                items = list(self.stellaris_lore[category].keys())
                embed.add_field(
                    name=f"🔍 {category.replace('_', ' ').title()}",
                    value=", ".join(
                        [item.replace("_", " ").title() for item in items[:5]]
                    )
                    + (f" (+{len(items)-5} more)" if len(items) > 5 else ""),
                    inline=False,
                )

            embed.add_field(
                name="💡 Examples",
                value="`/empire lore topic:dyson_sphere` • `/empire lore topic:prethoryn_scourge` • `/empire lore topic:void_dwellers`",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)
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
                color=self.config.get_color("error"),
            )

            if suggestions:
                embed.add_field(
                    name="💡 Did you mean?",
                    value="\n".join([f"`/empire lore topic:{s}`" for s in suggestions]),
                    inline=False,
                )

            embed.add_field(
                name="📚 Available Topics",
                value="Use `/empire lore` without a topic to see all available categories.",
                inline=False,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Display the lore
        embed = discord.Embed(
            title=f"📖 {topic.replace('_', ' ').title()}",
            description=found_lore,
            color=self.config.get_color("stellaris"),
            timestamp=datetime.now(timezone.utc),
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
                related_commands = [f"`/empire lore topic:{r}`" for r in related]
                embed.add_field(
                    name="🔗 Related Topics",
                    value=", ".join(related_commands),
                    inline=True,
                )

        embed.set_footer(
            text="🌌 Knowledge is power in the galaxy",
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="homeworld", description="Choose your homeworld planet type"
    )
    # @feature_enabled("stellaris_features")
    async def homeworld_command(self, interaction: discord.Interaction):
        """Choose your homeworld planet type"""
        # Create the homeworld selection view
        view = HomeworldSelectView()

        embed = discord.Embed(
            title="🌍 Choose Your Homeworld",
            description="Select the type of planet your species evolved on.\n\n"
            + "This selection is purely for roleplay and helps define your empire's background.",
            color=self.config.get_color("stellaris"),
        )

        # Show planet types
        embed.add_field(
            name="Planet Types",
            value="• 🌍 **Terran World**: Earth-like planet with balanced conditions\n"
            + "• 🏜️ **Desert World**: Arid planet with harsh, dry conditions\n"
            + "• 🌊 **Ocean World**: Water-covered planet with deep seas\n"
            + "• 🧊 **Arctic World**: Frozen planet with icy landscapes\n"
            + "• 🌴 **Jungle World**: Dense tropical world teeming with life\n"
            + "• 🌋 **Volcanic World**: Geologically active planet with lava flows\n"
            + "• 🪐 **Gas Giant Moon**: Moon orbiting a massive gas giant\n"
            + "• 🛰️ **Artificial World**: Constructed habitat or ring world",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="count", description="Show the count of members with each empire role"
    )
    @app_commands.checks.cooldown(1, 15)
    # @feature_enabled("stellaris_features.empire_roles")
    async def empire_role_count(self, interaction: discord.Interaction):
        """Show distribution of empire roles in the server"""
        await interaction.response.defer()

        embed = discord.Embed(
            title="📊 Stellaris Empire Census",
            description="Current distribution of empire roles in this server",
            color=self.config.get_color("stellaris"),
            timestamp=datetime.now(timezone.utc),
        )

        total_members = 0
        role_data = []

        for emoji, empire_data in self.empire_types.items():
            role = discord.utils.get(interaction.guild.roles, name=empire_data["name"])
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
                value="No members have chosen empire roles yet! Use `/empire choose` to get started.",
                inline=False,
            )

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="add_role", description="Add a custom empire role (Admin only)"
    )
    @app_commands.describe(
        role_name="Name of the role to create", emoji="Emoji for the role"
    )
    @app_commands.default_permissions(manage_roles=True)
    # @feature_enabled("stellaris_features.empire_roles")
    async def add_custom_role(
        self,
        interaction: discord.Interaction,
        role_name: str,
        emoji: Optional[str] = None,
    ):
        """Add a custom empire role (Admin only)"""
        # Check if user has permission
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ You need 'Manage Roles' permission to use this command.",
                ephemeral=True,
            )
            return

        # Check if role already exists
        existing_role = discord.utils.get(interaction.guild.roles, name=role_name)
        if existing_role:
            await interaction.response.send_message(
                f"❌ A role named '{role_name}' already exists in this server.",
                ephemeral=True,
            )
            return

        try:
            # Create the role
            role = await interaction.guild.create_role(
                name=role_name,
                color=discord.Color.random(),
                mentionable=True,
                reason=f"Custom empire role created by {interaction.user}",
            )

            embed = discord.Embed(
                title="✅ Role Created",
                description=f"Successfully created the **{role_name}** role!",
                color=self.config.get_color("success"),
            )

            embed.add_field(
                name="🎨 Role Details",
                value=f"**Name:** {role.name}\n**Color:** {role.color}\n**Mentionable:** Yes",
                inline=True,
            )

            # Add to empire types if emoji provided
            if emoji:
                self.empire_types[emoji] = {
                    "name": role_name,
                    "description": f"Custom empire role created by {interaction.user.display_name}",
                    "ethics": "Custom",
                    "government": "Custom",
                }

                embed.add_field(
                    name="🔄 Empire System",
                    value=f"Role added to empire selection with emoji {emoji}",
                    inline=True,
                )

            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create roles.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to create role: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Roles(bot))
