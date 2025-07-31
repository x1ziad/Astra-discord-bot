"""
Centralized embed formatting for Astra Bot
Provides consistent styling and formatting for all embeds
"""

import discord
from datetime import datetime
from typing import Optional, Dict, List, Any, Union

from config.config_manager import config_manager


class EmbedBuilder:
    """Builder class for creating consistently styled embeds"""

    @staticmethod
    def get_color(color_name: str = "primary") -> discord.Color:
        """Get color from palette"""
        color_int = config_manager.get_color(color_name)
        return discord.Color(color_int)

    @staticmethod
    def success(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create a success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=EmbedBuilder.get_color("success"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def error(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create an error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=EmbedBuilder.get_color("error"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def warning(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create a warning embed"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=EmbedBuilder.get_color("warning"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def info(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create an info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=EmbedBuilder.get_color("info"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def primary(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create a primary styled embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=EmbedBuilder.get_color("primary"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def space(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create a space themed embed"""
        embed = discord.Embed(
            title=f"🌌 {title}",
            description=description,
            color=EmbedBuilder.get_color("space"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def stellaris(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Create a Stellaris themed embed"""
        embed = discord.Embed(
            title=f"🏛️ {title}",
            description=description,
            color=EmbedBuilder.get_color("stellaris"),
            **kwargs,
        )

        if "timestamp" not in kwargs:
            embed.timestamp = datetime.utcnow()

        return embed

    @staticmethod
    def paginated_embeds(
        title: str,
        entries: List[str],
        description: str = None,
        color: str = "primary",
        items_per_page: int = 10,
        page_title_format: str = "Page {current_page}/{max_pages}",
        **kwargs,
    ) -> List[discord.Embed]:
        """Create paginated embeds from a list of entries"""
        embeds = []

        # Calculate total pages
        pages = [
            entries[i : i + items_per_page]
            for i in range(0, len(entries), items_per_page)
        ]
        max_pages = len(pages)

        # Create an embed for each page
        for i, page_entries in enumerate(pages):
            current_page = i + 1

            # Format the page title
            page_title = page_title_format.format(
                current_page=current_page, max_pages=max_pages
            )

            # Create the embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=EmbedBuilder.get_color(color),
                **kwargs,
            )

            # Add page number to footer
            if "footer" not in kwargs:
                embed.set_footer(text=page_title)

            # Add entries to the embed
            for entry in page_entries:
                if isinstance(entry, dict):
                    embed.add_field(
                        name=entry.get("name", "No Title"),
                        value=entry.get("value", "No Value"),
                        inline=entry.get("inline", False),
                    )
                else:
                    # If it's just a string, add it to the description
                    if embed.description:
                        embed.description += f"\n{entry}"
                    else:
                        embed.description = entry

            embeds.append(embed)

        return embeds


class HelpEmbed(discord.Embed):
    """Specialized embed for help commands"""

    def __init__(self, title: str = None, description: str = None, **kwargs):
        super().__init__(
            title=title or "Help",
            description=description or "Command information",
            color=EmbedBuilder.get_color("info"),
            **kwargs,
        )

        # Set default timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.utcnow()

    def add_command(
        self, name: str, syntax: str, description: str, inline: bool = False
    ) -> None:
        """Add a command to the help embed"""
        value = f"**Syntax:** `{syntax}`\n{description}"
        self.add_field(name=name, value=value, inline=inline)

    def add_group(
        self, name: str, commands: List[Dict[str, str]], inline: bool = False
    ) -> None:
        """Add a command group to the help embed"""
        value = "\n".join(
            [f"`{cmd['name']}` - {cmd['description']}" for cmd in commands]
        )
        self.add_field(name=name, value=value, inline=inline)

    def set_command_info(
        self,
        command_name: str,
        syntax: str,
        description: str,
        aliases: List[str] = None,
    ) -> None:
        """Set the main content of help embed for a specific command"""
        self.title = f"Command: /{command_name}"
        self.description = description

        # Add syntax field
        self.add_field(name="Syntax", value=f"```\n{syntax}\n```", inline=False)

        # Add aliases if any
        if aliases and len(aliases) > 0:
            self.add_field(
                name="Aliases",
                value=", ".join([f"`{alias}`" for alias in aliases]),
                inline=True,
            )
