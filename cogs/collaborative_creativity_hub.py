"""
Collaborative Creativity Hub Commands
Commands for collaborative creative projects and brainstorming
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ai.collaborative_creativity_hub import (
    get_creativity_hub,
    ProjectType,
    ProjectStatus,
    ProjectRole,
    IdeaStatus,
)
from ui.embeds import EmbedBuilder


class CollaborativeCreativityHubCommands(commands.Cog):
    """Commands for collaborative creativity hub"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.creativity_commands")

        # Initialize creativity hub
        self.creativity_hub = get_creativity_hub()

        self.logger.info("Collaborative Creativity Hub Commands cog loaded")

    @commands.group(name="create", aliases=["creativity", "hub"])
    async def creativity_group(self, ctx):
        """Collaborative creativity hub commands"""
        if ctx.invoked_subcommand is None:
            embed = EmbedBuilder.primary(
                title="🎨 Collaborative Creativity Hub",
                description=(
                    "Create and collaborate on amazing creative projects together!\n\n"
                    "**🎯 Available Commands:**\n"
                    "• `create project <type> <title> | <description>` - Start a new project\n"
                    "• `create list` - View all projects\n"
                    "• `create view <id>` - View project details\n"
                    "• `create join <id>` - Join a project\n"
                    "• `create milestone <project_id> <title> | <description>` - Add milestone\n"
                    "• `create idea <project_id> <idea>` - Add brainstorm idea\n"
                    "• `create vote <project_id> <idea_id> <up/down>` - Vote on ideas\n\n"
                    "**🎨 Project Types:** art, music, writing, coding, design, film, game, other\n\n"
                    "**✨ How It Works:**\n"
                    "→ Create projects and invite collaborators\n"
                    "→ Set milestones and track progress\n"
                    "→ Brainstorm ideas and vote on the best ones\n"
                    "→ Build amazing things together!"
                ),
            )
            embed.add_field(
                name="🚀 Getting Started",
                value="Start with `create project` and let your creativity flow!",
                inline=True,
            )
            embed.add_field(
                name="🤝 Collaboration",
                value="Invite others to join and contribute their unique talents.",
                inline=True,
            )
            embed.add_field(
                name="💡 Innovation",
                value="Brainstorm ideas and build something extraordinary together.",
                inline=True,
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="project", aliases=["new", "start"])
    async def create_project(
        self, ctx, project_type: str, *, title_and_description: str
    ):
        """Create a new creative project"""
        try:
            # Parse title and description
            if "|" in title_and_description:
                title, description = title_and_description.split("|", 1)
                title = title.strip()
                description = description.strip()
            else:
                title = title_and_description.strip()
                description = (
                    f"A collaborative {project_type} project created by the community."
                )

            # Validate project type
            try:
                proj_type = ProjectType(project_type.lower())
            except ValueError:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Project Type",
                    description=f"'{project_type}' is not a valid type. Available types: {', '.join([t.value for t in ProjectType])}",
                )
                await ctx.send(embed=embed)
                return

            # Create the project
            project = await self.creativity_hub.create_project(
                server_id=ctx.guild.id,
                creator_id=ctx.author.id,
                title=title,
                description=description,
                project_type=proj_type,
            )

            if project:
                embed = EmbedBuilder.success(
                    title=f"🎨 Project Created: {project.title}",
                    description=f"**Type:** {project.project_type.value.title()}\n\n{project.description}",
                )

                embed.add_field(
                    name="🆔 Project ID",
                    value=f"`{project.id}`",
                    inline=True,
                )

                embed.add_field(
                    name="👤 Project Leader",
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
                    value="• Add team members with `create join`\n"
                    "• Set milestones with `create milestone`\n"
                    "• Start brainstorming with `create idea`\n"
                    "• Invite collaborators to join the creative journey!",
                    inline=False,
                )

                embed.set_footer(
                    text=f"Use 'create view {project.id}' to see the full project"
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Project Creation Failed",
                    description="Unable to create the project. Please try again.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            embed = EmbedBuilder.error(
                title="❌ Project Creation Error",
                description=f"Unable to create project: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="list", aliases=["all", "show"])
    async def list_projects(self, ctx, status: str = None, project_type: str = None):
        """List all projects in the server"""
        try:
            # Parse filters
            status_filter = None
            type_filter = None

            if status:
                try:
                    status_filter = ProjectStatus(status.lower())
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Status",
                        description=f"'{status}' is not a valid status. Available: planning, active, on_hold, completed, cancelled",
                    )
                    await ctx.send(embed=embed)
                    return

            if project_type:
                try:
                    type_filter = ProjectType(project_type.lower())
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Project Type",
                        description=f"'{project_type}' is not a valid type. Available: {', '.join([t.value for t in ProjectType])}",
                    )
                    await ctx.send(embed=embed)
                    return

            projects = await self.creativity_hub.get_server_projects(
                ctx.guild.id, status_filter, type_filter
            )

            if not projects:
                filter_desc = ""
                if status_filter or type_filter:
                    filters = []
                    if status_filter:
                        filters.append(f"status: {status_filter.value}")
                    if type_filter:
                        filters.append(f"type: {type_filter.value}")
                    filter_desc = f" (filtered by {', '.join(filters)})"

                embed = EmbedBuilder.info(
                    title="🎨 No Projects Found",
                    description=f"No projects found in this server{filter_desc}.\n\n**Start one with:** `create project <type> <title> | <description>`",
                )
                await ctx.send(embed=embed)
                return

            embed = EmbedBuilder.primary(
                title=f"🎨 Server Projects ({len(projects)})",
                description="Amazing collaborative creative projects created by this community!",
            )

            for project in projects[:8]:  # Show up to 8 projects
                status_emoji = {
                    ProjectStatus.PLANNING: "📝",
                    ProjectStatus.ACTIVE: "🚀",
                    ProjectStatus.ON_HOLD: "⏸️",
                    ProjectStatus.COMPLETED: "✅",
                    ProjectStatus.CANCELLED: "❌",
                }.get(project.status, "❓")

                member_count = len(project.members)
                completion = project.completion_percentage

                embed.add_field(
                    name=f"{status_emoji} {project.title}",
                    value=f"**Type:** {project.project_type.value.title()}\n"
                    f"**ID:** `{project.id}`\n"
                    f"**Members:** {member_count}\n"
                    f"**Progress:** {completion}%\n"
                    f"**Status:** {project.status.value.title()}",
                    inline=True,
                )

            if len(projects) > 8:
                embed.add_field(
                    name="📄 More Projects",
                    value=f"There are {len(projects) - 8} more projects. Use `create view <id>` to see specific ones!",
                    inline=False,
                )

            embed.set_footer(
                text=f"Total Projects: {len(projects)} | Use 'create view <id>' to see details"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing projects: {e}")
            embed = EmbedBuilder.error(
                title="❌ Error Loading Projects",
                description=f"Unable to load projects: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="view", aliases=["details", "info"])
    async def view_project(self, ctx, project_id: str):
        """View detailed information about a project"""
        try:
            project = await self.creativity_hub.get_project(project_id)

            if not project:
                embed = EmbedBuilder.error(
                    title="❌ Project Not Found",
                    description=f"No project found with ID `{project_id}`.\n\n**Check the ID and try again, or use `create list` to see all projects.**",
                )
                await ctx.send(embed=embed)
                return

            # Update view count
            project.view_count += 1
            await self.creativity_hub.update_project(project)

            embed = EmbedBuilder.primary(
                title=f"🎨 {project.title}",
                description=f"**Type:** {project.project_type.value.title()}\n"
                f"**Status:** {project.status.value.title()}\n"
                f"**Progress:** {project.completion_percentage}%\n"
                f"**Created:** {project.created_at.strftime('%B %d, %Y')}\n"
                f"**Members:** {len(project.members)}/{project.max_members}",
            )

            # Show description
            embed.add_field(
                name="📝 Description",
                value=project.description[:500]
                + ("..." if len(project.description) > 500 else ""),
                inline=False,
            )

            # Show members
            if project.members:
                member_list = []
                for member in list(project.members.values())[:5]:  # Show up to 5
                    role_emoji = {
                        ProjectRole.LEADER: "👑",
                        ProjectRole.CONTRIBUTOR: "👤",
                        ProjectRole.REVIEWER: "👀",
                        ProjectRole.MENTOR: "🎓",
                        ProjectRole.COLLABORATOR: "🤝",
                    }.get(member.role, "❓")
                    member_list.append(f"{role_emoji} <@{member.user_id}>")

                if len(project.members) > 5:
                    member_list.append(f"*... and {len(project.members) - 5} more*")

                embed.add_field(
                    name=f"👥 Team ({len(project.members)})",
                    value="\n".join(member_list),
                    inline=True,
                )

            # Show milestones
            if project.milestones:
                milestone_list = []
                for milestone in list(project.milestones.values())[:3]:  # Show up to 3
                    status = "✅" if milestone.completed else "⏳"
                    milestone_list.append(f"{status} {milestone.title}")

                if len(project.milestones) > 3:
                    milestone_list.append(
                        f"*... and {len(project.milestones) - 3} more*"
                    )

                embed.add_field(
                    name=f"🎯 Milestones ({len(project.milestones)})",
                    value="\n".join(milestone_list),
                    inline=True,
                )

            # Show top ideas
            if project.ideas:
                top_ideas = sorted(
                    project.ideas.values(), key=lambda i: i.votes, reverse=True
                )[:3]
                idea_list = []
                for idea in top_ideas:
                    idea_list.append(
                        f"💡 {idea.content[:50]}{'...' if len(idea.content) > 50 else ''} ({idea.votes} votes)"
                    )

                embed.add_field(
                    name=f"💡 Top Ideas ({len(project.ideas)} total)",
                    value="\n".join(idea_list),
                    inline=False,
                )

            # Action buttons
            embed.add_field(
                name="🚀 Contribute",
                value=f"Join with: `create join {project.id}`",
                inline=True,
            )

            embed.add_field(
                name="💡 Brainstorm",
                value=f"Add ideas: `create idea {project.id} <your idea>`",
                inline=True,
            )

            embed.add_field(
                name="❤️ Favorite",
                value=f"Save project: `create favorite {project.id}`",
                inline=True,
            )

            embed.set_footer(
                text=f"Project ID: {project.id} | Views: {project.view_count} | Favorites: {project.favorite_count}"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error viewing project: {e}")
            embed = EmbedBuilder.error(
                title="❌ Error Loading Project",
                description=f"Unable to load project: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="join", aliases=["participate"])
    async def join_project(self, ctx, project_id: str, *, skills: str = None):
        """Join a creative project"""
        try:
            project = await self.creativity_hub.get_project(project_id)

            if not project:
                embed = EmbedBuilder.error(
                    title="❌ Project Not Found",
                    description=f"No project found with ID `{project_id}`.",
                )
                await ctx.send(embed=embed)
                return

            if ctx.author.id in project.members:
                embed = EmbedBuilder.info(
                    title="ℹ️ Already a Member",
                    description=f"You are already a member of **{project.title}**!",
                )
                await ctx.send(embed=embed)
                return

            if len(project.members) >= project.max_members:
                embed = EmbedBuilder.error(
                    title="❌ Project Full",
                    description=f"**{project.title}** has reached its maximum member limit of {project.max_members}.",
                )
                await ctx.send(embed=embed)
                return

            # Parse skills
            skill_list = []
            if skills:
                skill_list = [s.strip() for s in skills.split(",")]

            success = await self.creativity_hub.join_project(
                project_id, ctx.author.id, skill_list
            )

            if success:
                embed = EmbedBuilder.success(
                    title="🎉 Welcome to the Team!",
                    description=f"You have successfully joined **{project.title}**!",
                )

                embed.add_field(
                    name="🎨 Project Type",
                    value=project.project_type.value.title(),
                    inline=True,
                )

                embed.add_field(
                    name="👥 Team Size",
                    value=f"{len(project.members) + 1}/{project.max_members}",
                    inline=True,
                )

                if skill_list:
                    embed.add_field(
                        name="🛠️ Your Skills",
                        value=", ".join(skill_list),
                        inline=True,
                    )

                embed.add_field(
                    name="🚀 Get Started",
                    value="• Check out the project details with `create view`\n"
                    "• Add your ideas with `create idea`\n"
                    "• Help complete milestones\n"
                    "• Collaborate with your new teammates!",
                    inline=False,
                )

                embed.set_footer(
                    text=f"Welcome to {project.title}! Let's create something amazing together."
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Join Failed",
                    description="Unable to join the project. It may be full or there may be another issue.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error joining project: {e}")
            embed = EmbedBuilder.error(
                title="❌ Join Error",
                description=f"Unable to join project: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="milestone", aliases=["goal", "task"])
    async def add_milestone(self, ctx, project_id: str, *, title_and_description: str):
        """Add a milestone to a project"""
        try:
            project = await self.creativity_hub.get_project(project_id)

            if not project:
                embed = EmbedBuilder.error(
                    title="❌ Project Not Found",
                    description=f"No project found with ID `{project_id}`.",
                )
                await ctx.send(embed=embed)
                return

            # Check if user is a member
            if ctx.author.id not in project.members:
                embed = EmbedBuilder.error(
                    title="❌ Not a Team Member",
                    description="You must be a member of this project to add milestones.",
                )
                await ctx.send(embed=embed)
                return

            # Parse title and description
            if "|" in title_and_description:
                title, description = title_and_description.split("|", 1)
                title = title.strip()
                description = description.strip()
            else:
                title = title_and_description.strip()
                description = "Complete this milestone to advance the project."

            milestone = await self.creativity_hub.add_milestone(
                project_id=project_id,
                title=title,
                description=description,
            )

            if milestone:
                embed = EmbedBuilder.success(
                    title="🎯 Milestone Added!",
                    description=f"Successfully added milestone to **{project.title}**!",
                )

                embed.add_field(
                    name="📝 Milestone",
                    value=f"**{milestone.title}**\n{milestone.description}",
                    inline=False,
                )

                embed.add_field(
                    name="🆔 Milestone ID",
                    value=f"`{milestone.id}`",
                    inline=True,
                )

                embed.add_field(
                    name="📊 Progress",
                    value=f"Project completion: {project.completion_percentage}%",
                    inline=True,
                )

                embed.set_footer(text=f"Milestone added to {project.title}")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Milestone Creation Failed",
                    description="Unable to add milestone to the project.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error adding milestone: {e}")
            embed = EmbedBuilder.error(
                title="❌ Milestone Error",
                description=f"Unable to add milestone: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="idea", aliases=["brainstorm", "suggest"])
    async def add_idea(self, ctx, project_id: str, *, idea_content: str):
        """Add a brainstorm idea to a project"""
        try:
            project = await self.creativity_hub.get_project(project_id)

            if not project:
                embed = EmbedBuilder.error(
                    title="❌ Project Not Found",
                    description=f"No project found with ID `{project_id}`.",
                )
                await ctx.send(embed=embed)
                return

            # Check if user is a member
            if ctx.author.id not in project.members:
                embed = EmbedBuilder.error(
                    title="❌ Not a Team Member",
                    description="You must be a member of this project to add ideas.",
                )
                await ctx.send(embed=embed)
                return

            idea = await self.creativity_hub.add_brainstorm_idea(
                project_id=project_id,
                author_id=ctx.author.id,
                content=idea_content,
            )

            if idea:
                embed = EmbedBuilder.success(
                    title="💡 Idea Added!",
                    description=f"Your brainstorm idea has been added to **{project.title}**!",
                )

                embed.add_field(
                    name="💭 Your Idea",
                    value=idea_content[:500]
                    + ("..." if len(idea_content) > 500 else ""),
                    inline=False,
                )

                embed.add_field(
                    name="🆔 Idea ID",
                    value=f"`{idea.id}`",
                    inline=True,
                )

                embed.add_field(
                    name="🗳️ Current Votes",
                    value="0 (be the first to vote!)",
                    inline=True,
                )

                embed.add_field(
                    name="🚀 Next Steps",
                    value="• Community members can vote on your idea\n"
                    "• Use `create vote` to vote on other ideas\n"
                    "• Ideas with the most votes may be implemented!",
                    inline=False,
                )

                embed.set_footer(
                    text=f"Idea added to {project.title} - let's build something amazing!"
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Idea Submission Failed",
                    description="Unable to add your idea to the project.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error adding idea: {e}")
            embed = EmbedBuilder.error(
                title="❌ Idea Error",
                description=f"Unable to add idea: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="vote", aliases=["upvote", "downvote"])
    async def vote_on_idea(self, ctx, project_id: str, idea_id: str, vote_type: str):
        """Vote on a brainstorm idea"""
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

            success = await self.creativity_hub.vote_on_idea(
                project_id=project_id,
                idea_id=idea_id,
                user_id=ctx.author.id,
                vote_up=vote_up,
            )

            if success:
                emoji = "👍" if vote_up else "👎"
                vote_word = "upvote" if vote_up else "downvote"

                embed = EmbedBuilder.success(
                    title=f"{emoji} Vote Recorded!",
                    description=f"Your {vote_word} has been recorded for idea `{idea_id}` in project `{project_id}`.",
                )

                embed.add_field(
                    name="🗳️ Your Vote",
                    value=f"**{vote_word.title()}** {emoji}",
                    inline=True,
                )

                embed.add_field(
                    name="💡 Impact",
                    value="Your vote helps determine which ideas become part of the project!",
                    inline=False,
                )

                embed.set_footer(
                    text="Thank you for participating in the collaborative brainstorming process!"
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Vote Failed",
                    description="Unable to record your vote. The project or idea may not exist, or you may have already voted.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error voting on idea: {e}")
            embed = EmbedBuilder.error(
                title="❌ Voting Error",
                description=f"Unable to process vote: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="favorite", aliases=["fav", "save"])
    async def toggle_favorite(self, ctx, project_id: str):
        """Toggle favorite status for a project"""
        try:
            added = await self.creativity_hub.toggle_favorite(project_id, ctx.author.id)

            if added:
                embed = EmbedBuilder.success(
                    title="❤️ Project Favorited!",
                    description=f"You have added project `{project_id}` to your favorites.",
                )

                embed.add_field(
                    name="📚 Your Favorites",
                    value="You can now easily find this project in your favorite projects list!",
                    inline=False,
                )
            else:
                embed = EmbedBuilder.info(
                    title="💔 Project Unfavorited",
                    description=f"You have removed project `{project_id}` from your favorites.",
                )

                embed.add_field(
                    name="📚 Your Favorites",
                    value="The project has been removed from your favorites list.",
                    inline=False,
                )

            embed.set_footer(
                text="Use 'create favorites' to see all your favorited projects"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error toggling favorite: {e}")
            embed = EmbedBuilder.error(
                title="❌ Favorite Error",
                description=f"Unable to update favorite status: {str(e)}",
            )
            await ctx.send(embed=embed)

    @creativity_group.command(name="stats", aliases=["statistics", "analytics"])
    async def creativity_stats(self, ctx):
        """View creativity hub statistics for the server"""
        try:
            stats = await self.creativity_hub.get_project_stats(ctx.guild.id)

            embed = EmbedBuilder.primary(
                title="📊 Server Creativity Statistics",
                description="How this community creates amazing collaborative projects!",
            )

            embed.add_field(
                name="🎨 Project Portfolio",
                value=f"**Total Projects:** {stats['total_projects']}\n"
                f"**Active Projects:** {stats['active_projects']}\n"
                f"**Completed Projects:** {stats['completed_projects']}",
                inline=True,
            )

            embed.add_field(
                name="👥 Community Collaboration",
                value=f"**Total Contributors:** {stats['total_members']}\n"
                f"**Total Milestones:** {stats['total_milestones']}\n"
                f"**Total Ideas:** {stats['total_ideas']}",
                inline=True,
            )

            embed.add_field(
                name="🚀 Creative Insights",
                value=f"**Most Popular Type:** {stats['most_popular_type'] or 'None yet'}\n"
                f"**Avg Completion:** {stats['average_completion']}%\n"
                f"**Collaboration Rate:** {stats['total_members']/max(1, stats['total_projects']):.1f} contributors/project",
                inline=True,
            )

            embed.add_field(
                name="✨ Community Creativity",
                value="• Projects bring people together through shared creative goals\n"
                "• Every idea contributes to building something extraordinary\n"
                "• Collaborative creation fosters deeper community connections\n"
                "• Creative expression strengthens community bonds",
                inline=False,
            )

            embed.set_footer(
                text=f"Server: {ctx.guild.name} | Keep creating amazing projects together!"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error getting creativity stats: {e}")
            embed = EmbedBuilder.error(
                title="❌ Statistics Error",
                description=f"Unable to load statistics: {str(e)}",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(CollaborativeCreativityHubCommands(bot))
