"""
Interactive Storytelling Commands
Provides commands for collaborative story creation and management
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ai.interactive_storytelling import (
    get_storytelling_engine,
    StoryGenre,
    StoryStatus,
    ContributionType,
)
from ui.embeds import EmbedBuilder


class InteractiveStorytellingCommands(commands.Cog):
    """Commands for interactive storytelling"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.storytelling")

        # Initialize storytelling engine
        self.storytelling_engine = get_storytelling_engine()

        self.logger.info("Interactive Storytelling Commands cog loaded")

    @commands.group(name="story", aliases=["stories", "tale"])
    async def story_group(self, ctx):
        """Interactive storytelling commands"""
        if ctx.invoked_subcommand is None:
            embed = EmbedBuilder.primary(
                title="📖 Interactive Storytelling",
                description=(
                    "Create collaborative stories with your community!\n\n"
                    "**🎭 Available Commands:**\n"
                    "• `story create <title> <genre>` - Start a new story\n"
                    "• `story list` - View all stories\n"
                    "• `story view <id>` - Read a story\n"
                    "• `story contribute <id> <content>` - Add to a story\n"
                    "• `story characters <id>` - Manage story characters\n"
                    "• `story vote <story_id> <contrib_id> <up/down>` - Vote on contributions\n"
                    "• `story accept <story_id> <contrib_id>` - Accept contribution (admin)\n\n"
                    "**📚 Genres:** fantasy, sci-fi, mystery, romance, horror, adventure, comedy, drama, mixed\n\n"
                    "**✨ How It Works:**\n"
                    "→ Create a story with a premise\n"
                    "→ Community members contribute plot points, dialogue, and descriptions\n"
                    "→ Vote on the best contributions\n"
                    "→ Build amazing stories together!"
                ),
            )
            embed.add_field(
                name="🎯 Story Creation",
                value="Start with `story create` and let your imagination run wild!",
                inline=True,
            )
            embed.add_field(
                name="🤝 Collaborative Writing",
                value="Everyone can contribute their unique perspective and creativity.",
                inline=True,
            )
            embed.add_field(
                name="⭐ Community Building",
                value="Stories bring people together through shared creativity.",
                inline=True,
            )
            await ctx.send(embed=embed)

    @story_group.command(name="create", aliases=["new", "start"])
    async def create_story(self, ctx, genre: str, *, title_and_description: str):
        """Create a new interactive story"""
        try:
            # Parse title and description
            if "|" in title_and_description:
                title, description = title_and_description.split("|", 1)
                title = title.strip()
                description = description.strip()
            else:
                title = title_and_description.strip()
                description = f"A {genre} story created by the community."

            # Validate genre
            try:
                story_genre = StoryGenre(genre.lower())
            except ValueError:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Genre",
                    description=f"'{genre}' is not a valid genre. Available genres: {', '.join([g.value for g in StoryGenre])}",
                )
                await ctx.send(embed=embed)
                return

            # Create the story
            story = await self.storytelling_engine.create_story(
                server_id=ctx.guild.id,
                creator_id=ctx.author.id,
                title=title,
                description=description,
                genre=story_genre,
            )

            embed = EmbedBuilder.success(
                title=f"📖 Story Created: {story.title}",
                description=f"**Genre:** {story.genre.value.title()}\n\n{story.description}",
            )

            embed.add_field(
                name="🎭 Story ID",
                value=f"`{story.id}`",
                inline=True,
            )

            embed.add_field(
                name="👤 Created By",
                value=ctx.author.mention,
                inline=True,
            )

            embed.add_field(
                name="📊 Status",
                value="Planning Phase",
                inline=True,
            )

            embed.add_field(
                name="🚀 Next Steps",
                value="• Add characters with `story characters add`\n"
                "• Start writing with `story contribute`\n"
                "• Invite others to join the creative journey!",
                inline=False,
            )

            embed.set_footer(text=f"Use 'story view {story.id}' to see the full story")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error creating story: {e}")
            embed = EmbedBuilder.error(
                title="❌ Story Creation Failed",
                description=f"Unable to create story: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="list", aliases=["all", "show"])
    async def list_stories(self, ctx, status: str = None):
        """List all stories in the server"""
        try:
            # Parse status filter
            status_filter = None
            if status:
                try:
                    status_filter = StoryStatus(status.lower())
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Status",
                        description=f"'{status}' is not a valid status. Available: planning, writing, reviewing, completed, archived",
                    )
                    await ctx.send(embed=embed)
                    return

            stories = await self.storytelling_engine.get_server_stories(
                ctx.guild.id, status_filter
            )

            if not stories:
                embed = EmbedBuilder.info(
                    title="📚 No Stories Found",
                    description="No stories have been created in this server yet.\n\n**Start one with:** `story create <genre> <title> | <description>`",
                )
                await ctx.send(embed=embed)
                return

            embed = EmbedBuilder.primary(
                title=f"📖 Server Stories ({len(stories)})",
                description="All the amazing collaborative stories created by this community!",
            )

            for story in stories[:10]:  # Show up to 10 stories
                status_emoji = {
                    StoryStatus.PLANNING: "📝",
                    StoryStatus.WRITING: "✍️",
                    StoryStatus.REVIEWING: "👀",
                    StoryStatus.COMPLETED: "✅",
                    StoryStatus.ARCHIVED: "📦",
                }.get(story.status, "❓")

                contributors = len(story.contributors)
                word_count = story.word_count

                embed.add_field(
                    name=f"{status_emoji} {story.title}",
                    value=f"**Genre:** {story.genre.value.title()}\n"
                    f"**ID:** `{story.id}`\n"
                    f"**Contributors:** {contributors}\n"
                    f"**Words:** {word_count:,}\n"
                    f"**Status:** {story.status.value.title()}",
                    inline=True,
                )

            if len(stories) > 10:
                embed.add_field(
                    name="📄 More Stories",
                    value=f"There are {len(stories) - 10} more stories. Use `story view <id>` to read specific ones!",
                    inline=False,
                )

            embed.set_footer(
                text=f"Total Stories: {len(stories)} | Use 'story view <id>' to read a story"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing stories: {e}")
            embed = EmbedBuilder.error(
                title="❌ Error Loading Stories",
                description=f"Unable to load stories: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="view", aliases=["read"])
    async def view_story(self, ctx, story_id: str):
        """View a specific story"""
        try:
            story = await self.storytelling_engine.get_story(story_id)

            if not story:
                embed = EmbedBuilder.error(
                    title="❌ Story Not Found",
                    description=f"No story found with ID `{story_id}`.\n\n**Check the ID and try again, or use `story list` to see all stories.**",
                )
                await ctx.send(embed=embed)
                return

            # Update view count
            story.view_count += 1
            await self.storytelling_engine._save_story(story)

            embed = EmbedBuilder.primary(
                title=f"📖 {story.title}",
                description=f"**Genre:** {story.genre.value.title()}\n"
                f"**Status:** {story.status.value.title()}\n"
                f"**Created:** {story.created_at.strftime('%B %d, %Y')}\n"
                f"**Contributors:** {len(story.contributors)}\n"
                f"**Total Words:** {story.word_count:,}",
            )

            # Show story content
            full_text = story.get_full_story_text()

            # Truncate if too long for Discord embed
            if len(full_text) > 4000:
                truncated_text = (
                    full_text[:4000]
                    + "...\n\n*(Story truncated - too long for Discord)*"
                )
                embed.add_field(
                    name="📄 Story Content (Partial)",
                    value=truncated_text,
                    inline=False,
                )
            else:
                embed.add_field(
                    name="📄 Story Content",
                    value=full_text,
                    inline=False,
                )

            # Show pending contributions if any
            pending = story.get_pending_contributions()
            if pending:
                pending_info = f"There are {len(pending)} pending contributions waiting for votes/approval."
                embed.add_field(
                    name="⏳ Pending Contributions",
                    value=pending_info,
                    inline=False,
                )

            # Show characters if any
            if story.characters:
                char_list = []
                for char in list(story.characters.values())[:5]:  # Show up to 5
                    char_list.append(f"• **{char.name}**: {char.description[:100]}...")

                if len(story.characters) > 5:
                    char_list.append(f"*... and {len(story.characters) - 5} more*")

                embed.add_field(
                    name=f"👥 Characters ({len(story.characters)})",
                    value="\n".join(char_list),
                    inline=False,
                )

            embed.add_field(
                name="🎯 Contribute",
                value=f"Add to this story with: `story contribute {story.id} <your contribution>`",
                inline=True,
            )

            embed.add_field(
                name="❤️ Favorite",
                value=f"Save this story: `story favorite {story.id}`",
                inline=True,
            )

            embed.add_field(
                name="📊 Stats",
                value=f"Views: {story.view_count}\nFavorites: {story.favorite_count}",
                inline=True,
            )

            embed.set_footer(text=f"Story ID: {story.id} | Created by community member")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error viewing story: {e}")
            embed = EmbedBuilder.error(
                title="❌ Error Loading Story",
                description=f"Unable to load story: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="contribute", aliases=["add", "write"])
    async def contribute_to_story(self, ctx, story_id: str, *, content: str):
        """Contribute to a story"""
        try:
            story = await self.storytelling_engine.get_story(story_id)

            if not story:
                embed = EmbedBuilder.error(
                    title="❌ Story Not Found",
                    description=f"No story found with ID `{story_id}`.",
                )
                await ctx.send(embed=embed)
                return

            if story.status not in [StoryStatus.WRITING, StoryStatus.PLANNING]:
                embed = EmbedBuilder.error(
                    title="❌ Story Not Accepting Contributions",
                    description=f"This story is {story.status.value} and not accepting new contributions.",
                )
                await ctx.send(embed=embed)
                return

            # Check word count
            word_count = len(content.split())
            if word_count < story.min_words_per_contribution:
                embed = EmbedBuilder.error(
                    title="❌ Contribution Too Short",
                    description=f"Your contribution must be at least {story.min_words_per_contribution} words. Yours has {word_count} words.",
                )
                await ctx.send(embed=embed)
                return

            if word_count > story.max_words_per_contribution:
                embed = EmbedBuilder.error(
                    title="❌ Contribution Too Long",
                    description=f"Your contribution must be no more than {story.max_words_per_contribution} words. Yours has {word_count} words.",
                )
                await ctx.send(embed=embed)
                return

            # Add contribution
            contribution = await self.storytelling_engine.add_contribution(
                story_id=story_id,
                contributor_id=ctx.author.id,
                contribution_type=ContributionType.PLOT_POINT,  # Default type
                content=content,
            )

            if contribution:
                embed = EmbedBuilder.success(
                    title="✍️ Contribution Added!",
                    description=f"Your contribution has been added to **{story.title}**!",
                )

                embed.add_field(
                    name="📝 Your Contribution",
                    value=f"{content[:500]}{'...' if len(content) > 500 else ''}",
                    inline=False,
                )

                embed.add_field(
                    name="📊 Details",
                    value=f"**Words:** {word_count}\n"
                    f"**Contribution ID:** `{contribution.id}`\n"
                    f"**Status:** Pending Review",
                    inline=True,
                )

                if story.voting_enabled:
                    embed.add_field(
                        name="🗳️ Next Steps",
                        value="• Community members can vote on your contribution\n"
                        "• If it gets enough positive votes, it will be accepted\n"
                        "• Check back later to see if it's been added to the story!",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="👑 Awaiting Approval",
                        value="The story creator or moderators will review your contribution and decide whether to include it in the story.",
                        inline=False,
                    )

                embed.set_footer(text=f"Thank you for contributing to {story.title}!")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Contribution Failed",
                    description="Unable to add your contribution. You may have reached the contributor limit or there may be another issue.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error adding contribution: {e}")
            embed = EmbedBuilder.error(
                title="❌ Contribution Error",
                description=f"Unable to add contribution: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="characters", aliases=["chars", "people"])
    async def manage_characters(
        self, ctx, action: str, story_id: str, *, details: str = None
    ):
        """Manage story characters"""
        try:
            story = await self.storytelling_engine.get_story(story_id)

            if not story:
                embed = EmbedBuilder.error(
                    title="❌ Story Not Found",
                    description=f"No story found with ID `{story_id}`.",
                )
                await ctx.send(embed=embed)
                return

            if action.lower() == "list":
                # List all characters
                if not story.characters:
                    embed = EmbedBuilder.info(
                        title=f"👥 Characters in {story.title}",
                        description="No characters have been created for this story yet.\n\n**Add one with:** `story characters add <story_id> <name> | <description>`",
                    )
                else:
                    embed = EmbedBuilder.primary(
                        title=f"👥 Characters in {story.title} ({len(story.characters)})",
                        description="All the fascinating characters in this story!",
                    )

                    for char in story.characters.values():
                        traits_str = (
                            ", ".join(char.traits)
                            if char.traits
                            else "No traits defined"
                        )
                        embed.add_field(
                            name=f"**{char.name}**",
                            value=f"{char.description}\n\n**Traits:** {traits_str}\n**Created by:** <@{char.created_by}>",
                            inline=False,
                        )

                await ctx.send(embed=embed)

            elif action.lower() == "add":
                if not details:
                    embed = EmbedBuilder.error(
                        title="❌ Missing Character Details",
                        description="Please provide character details in format: `name | description`",
                    )
                    await ctx.send(embed=embed)
                    return

                if "|" not in details:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Format",
                        description="Please use format: `story characters add <story_id> <name> | <description>`",
                    )
                    await ctx.send(embed=embed)
                    return

                name, description = details.split("|", 1)
                name = name.strip()
                description = description.strip()

                character = await self.storytelling_engine.add_character(
                    story_id=story_id,
                    creator_id=ctx.author.id,
                    name=name,
                    description=description,
                )

                if character:
                    embed = EmbedBuilder.success(
                        title="👤 Character Added!",
                        description=f"**{character.name}** has been added to **{story.title}**!",
                    )

                    embed.add_field(
                        name="📝 Description",
                        value=character.description,
                        inline=False,
                    )

                    embed.add_field(
                        name="🎭 Character ID",
                        value=f"`{character.id}`",
                        inline=True,
                    )

                    embed.add_field(
                        name="👤 Created By",
                        value=ctx.author.mention,
                        inline=True,
                    )

                    embed.set_footer(text=f"Character added to {story.title}")
                    await ctx.send(embed=embed)
                else:
                    embed = EmbedBuilder.error(
                        title="❌ Character Creation Failed",
                        description="Unable to add character to the story.",
                    )
                    await ctx.send(embed=embed)

            else:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Action",
                    description="Available actions: `list`, `add`",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error managing characters: {e}")
            embed = EmbedBuilder.error(
                title="❌ Character Management Error",
                description=f"Unable to manage characters: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="vote", aliases=["upvote", "downvote"])
    async def vote_on_contribution(
        self, ctx, story_id: str, contribution_id: str, vote_type: str
    ):
        """Vote on a story contribution"""
        try:
            # Validate vote type
            if vote_type.lower() not in ["up", "down", "upvote", "downvote"]:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Vote Type",
                    description="Please use `up`, `down`, `upvote`, or `downvote`.",
                )
                await ctx.send(embed=embed)
                return

            vote_up = vote_type.lower() in ["up", "upvote"]

            # Cast vote
            success = await self.storytelling_engine.vote_on_contribution(
                story_id=story_id,
                contribution_id=contribution_id,
                user_id=ctx.author.id,
                vote_up=vote_up,
            )

            if success:
                emoji = "👍" if vote_up else "👎"
                vote_word = "upvote" if vote_up else "downvote"

                embed = EmbedBuilder.success(
                    title=f"{emoji} Vote Recorded!",
                    description=f"Your {vote_word} has been recorded for contribution `{contribution_id}` in story `{story_id}`.",
                )

                embed.add_field(
                    name="🗳️ Your Vote",
                    value=f"**{vote_word.title()}** {emoji}",
                    inline=True,
                )

                embed.add_field(
                    name="📊 Impact",
                    value="Your vote helps determine which contributions become part of the story!",
                    inline=False,
                )

                embed.set_footer(
                    text="Thank you for participating in the collaborative storytelling process!"
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Vote Failed",
                    description="Unable to record your vote. The story or contribution may not exist, or voting may not be enabled.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error voting on contribution: {e}")
            embed = EmbedBuilder.error(
                title="❌ Voting Error",
                description=f"Unable to process vote: {str(e)}",
            )
            await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @story_group.command(name="accept", aliases=["approve"])
    async def accept_contribution(self, ctx, story_id: str, contribution_id: str):
        """Accept a contribution into the story (admin only)"""
        try:
            success = await self.storytelling_engine.accept_contribution(
                story_id=story_id, contribution_id=contribution_id
            )

            if success:
                embed = EmbedBuilder.success(
                    title="✅ Contribution Accepted!",
                    description=f"Contribution `{contribution_id}` has been accepted into story `{story_id}`.",
                )

                embed.add_field(
                    name="📖 Story Updated",
                    value="The contribution is now part of the official story!",
                    inline=False,
                )

                embed.add_field(
                    name="👀 View Story",
                    value=f"Use `story view {story_id}` to see the updated story.",
                    inline=False,
                )

                embed.set_footer(text="Contribution successfully added to the story")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Acceptance Failed",
                    description="Unable to accept the contribution. It may not exist or may already be accepted.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error accepting contribution: {e}")
            embed = EmbedBuilder.error(
                title="❌ Acceptance Error",
                description=f"Unable to accept contribution: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="favorite", aliases=["fav", "save"])
    async def toggle_favorite(self, ctx, story_id: str):
        """Toggle favorite status for a story"""
        try:
            added = await self.storytelling_engine.toggle_favorite(
                story_id=story_id, user_id=ctx.author.id
            )

            if added:
                embed = EmbedBuilder.success(
                    title="❤️ Story Favorited!",
                    description=f"You have added story `{story_id}` to your favorites.",
                )

                embed.add_field(
                    name="📚 Your Favorites",
                    value="You can now easily find this story in your favorite stories list!",
                    inline=False,
                )
            else:
                embed = EmbedBuilder.info(
                    title="💔 Story Unfavorited",
                    description=f"You have removed story `{story_id}` from your favorites.",
                )

                embed.add_field(
                    name="📚 Your Favorites",
                    value="The story has been removed from your favorites list.",
                    inline=False,
                )

            embed.set_footer(
                text="Use 'story favorites' to see all your favorited stories"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error toggling favorite: {e}")
            embed = EmbedBuilder.error(
                title="❌ Favorite Error",
                description=f"Unable to update favorite status: {str(e)}",
            )
            await ctx.send(embed=embed)

    @story_group.command(name="stats", aliases=["statistics", "info"])
    async def story_stats(self, ctx):
        """View storytelling statistics for the server"""
        try:
            stats = await self.storytelling_engine.get_story_stats(ctx.guild.id)

            embed = EmbedBuilder.primary(
                title="📊 Server Storytelling Statistics",
                description="How this community creates amazing stories together!",
            )

            embed.add_field(
                name="📚 Story Library",
                value=f"**Total Stories:** {stats['total_stories']}\n"
                f"**Active Stories:** {stats['active_stories']}\n"
                f"**Completed Stories:** {stats['completed_stories']}",
                inline=True,
            )

            embed.add_field(
                name="✍️ Community Writing",
                value=f"**Total Contributions:** {stats['total_contributions']:,}\n"
                f"**Total Words:** {stats['total_words']:,}\n"
                f"**Unique Contributors:** {stats['unique_contributors']}",
                inline=True,
            )

            embed.add_field(
                name="🎭 Creative Insights",
                value=f"**Most Popular Genre:** {stats['most_popular_genre'] or 'None yet'}\n"
                f"**Avg Story Length:** {stats['average_story_length']:.0f} words\n"
                f"**Collaboration Rate:** {stats['unique_contributors']/max(1, stats['total_stories']):.1f} contributors/story",
                inline=True,
            )

            embed.add_field(
                name="🚀 Community Creativity",
                value="• Stories bring people together through shared imagination\n"
                "• Every contribution adds a unique voice to the narrative\n"
                "• Collaborative writing builds stronger community bonds\n"
                "• Creative expression fosters deeper connections",
                inline=False,
            )

            embed.set_footer(
                text=f"Server: {ctx.guild.name} | Keep creating amazing stories together!"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error getting story stats: {e}")
            embed = EmbedBuilder.error(
                title="❌ Statistics Error",
                description=f"Unable to load statistics: {str(e)}",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(InteractiveStorytellingCommands(bot))
