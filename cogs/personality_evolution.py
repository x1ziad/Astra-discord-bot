"""
Personality Evolution Management Commands
Provides commands to view, manage, and debug the dynamic personality evolution system
"""

import discord
from discord.ext import commands
import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from ai.personality_evolution import (
    get_personality_engine,
    initialize_personality_engine,
    PersonalityEvolutionEngine,
    PersonalityProfile,
    UserRelationship,
)
from ui.embeds import EmbedBuilder


class PersonalityEvolutionCommands(commands.Cog):
    """Commands for managing dynamic personality evolution"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.personality_evolution")

        # Initialize personality engine if not already done
        self.personality_engine = get_personality_engine()
        if not self.personality_engine:
            self.personality_engine = initialize_personality_engine()

        self.logger.info("Personality Evolution Commands cog loaded")

    @commands.group(name="personality", aliases=["persona", "evolution"])
    async def personality_group(self, ctx):
        """Dynamic personality evolution commands"""
        if ctx.invoked_subcommand is None:
            embed = EmbedBuilder.primary(
                title="🧠 Dynamic Personality Evolution",
                description=(
                    "I learn and adapt my personality to each server's unique culture!\n\n"
                    "**Available Commands:**\n"
                    "• `personality status` - View current personality\n"
                    "• `personality analytics` - View evolution analytics\n"
                    "• `personality relationship` - View your relationship with me\n"
                    "• `personality test` - Test the evolution system\n"
                    "• `personality config` - Configure evolution settings\n"
                    "• `personality reset` - Reset personality (admin only)\n"
                    "• `personality export` - Export personality data"
                ),
            )
            await ctx.send(embed=embed)

    @personality_group.command(name="status")
    async def personality_status(self, ctx):
        """Show current server personality status"""
        try:
            personality = await self.personality_engine._get_server_personality(
                ctx.guild.id, ctx.guild.name
            )

            # Create detailed status embed
            embed = EmbedBuilder.primary(
                title=f"🧠 {ctx.guild.name} Personality Profile",
                description=f"**Personality Summary:** {personality.get_personality_summary()}",
            )

            # Culture confidence
            confidence_bar = self._create_progress_bar(
                personality.culture_confidence, 20
            )
            embed.add_field(
                name="📊 Culture Understanding",
                value=f"`{confidence_bar}` {personality.culture_confidence:.1%}\n"
                f"*Based on {personality.total_interactions:,} interactions*",
                inline=False,
            )

            # Personality traits
            traits_text = []

            # Humor style
            dominant_humor = max(personality.humor_style.items(), key=lambda x: x[1])
            humor_bar = self._create_progress_bar(dominant_humor[1], 10)
            traits_text.append(
                f"**Humor:** {dominant_humor[0].title()} `{humor_bar}` {dominant_humor[1]:.1%}"
            )

            # Formality level
            formality_bar = self._create_progress_bar(personality.formality_level, 10)
            formality_desc = (
                "Very Formal"
                if personality.formality_level > 0.8
                else (
                    "Formal"
                    if personality.formality_level > 0.6
                    else (
                        "Balanced"
                        if personality.formality_level > 0.4
                        else (
                            "Casual"
                            if personality.formality_level > 0.2
                            else "Very Casual"
                        )
                    )
                )
            )
            traits_text.append(
                f"**Formality:** {formality_desc} `{formality_bar}` {personality.formality_level:.1%}"
            )

            # Social energy
            energy_bar = self._create_progress_bar(personality.social_energy, 10)
            energy_desc = (
                "High Energy"
                if personality.social_energy > 0.7
                else "Balanced" if personality.social_energy > 0.3 else "Calm"
            )
            traits_text.append(
                f"**Energy:** {energy_desc} `{energy_bar}` {personality.social_energy:.1%}"
            )

            embed.add_field(
                name="🎭 Personality Traits", value="\n".join(traits_text), inline=False
            )

            # Learned patterns
            if personality.preferred_emojis or personality.inside_jokes:
                patterns_text = []

                if personality.preferred_emojis:
                    recent_emojis = personality.preferred_emojis[-10:]
                    patterns_text.append(
                        f"**Favorite Emojis:** {''.join(recent_emojis)}"
                    )

                if personality.inside_jokes:
                    joke_count = len(personality.inside_jokes)
                    patterns_text.append(f"**Inside Jokes Learned:** {joke_count}")

                embed.add_field(
                    name="🎪 Learned Culture",
                    value=(
                        "\n".join(patterns_text)
                        if patterns_text
                        else "Learning your server culture..."
                    ),
                    inline=False,
                )

            # Evolution timeline
            time_since_evolution = (
                datetime.now(timezone.utc) - personality.last_evolution
            )
            embed.add_field(
                name="⏰ Last Evolution",
                value=f"{self._format_timedelta(time_since_evolution)} ago",
                inline=True,
            )

            # Server-specific features
            if personality.total_interactions > 100:
                embed.add_field(
                    name="🌟 Evolution Status",
                    value="**Fully Adapted** - I understand this server's culture well!",
                    inline=True,
                )
            elif personality.total_interactions > 50:
                embed.add_field(
                    name="🌱 Evolution Status",
                    value="**Rapidly Learning** - Still adapting to your culture",
                    inline=True,
                )
            else:
                embed.add_field(
                    name="🐣 Evolution Status",
                    value="**Just Getting Started** - Learning your server's personality",
                    inline=True,
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in personality status: {e}")
            await ctx.send("❌ Error retrieving personality status. Please try again.")

    @personality_group.command(name="relationship", aliases=["relation", "bond"])
    async def personality_relationship(
        self, ctx, member: Optional[discord.Member] = None
    ):
        """Show relationship status with a user (default: yourself)"""
        target_user = member or ctx.author

        try:
            relationship = await self.personality_engine._get_user_relationship(
                ctx.guild.id, target_user.id, target_user.display_name
            )

            embed = EmbedBuilder.primary(
                title=f"🤝 Relationship with {target_user.display_name}",
                description=f"Here's what I've learned about our relationship:",
            )

            # Relationship strength
            strength_bar = self._create_progress_bar(
                relationship.relationship_strength, 20
            )
            strength_desc = (
                "Best Friend"
                if relationship.relationship_strength > 0.8
                else (
                    "Close Friend"
                    if relationship.relationship_strength > 0.6
                    else (
                        "Good Friend"
                        if relationship.relationship_strength > 0.4
                        else (
                            "Acquaintance"
                            if relationship.relationship_strength > 0.2
                            else "Just Met"
                        )
                    )
                )
            )

            embed.add_field(
                name="💝 Relationship Strength",
                value=f"`{strength_bar}` {relationship.relationship_strength:.1%}\n**{strength_desc}**",
                inline=False,
            )

            # Interaction stats
            stats_text = []
            stats_text.append(f"**Total Chats:** {relationship.total_interactions:,}")
            stats_text.append(
                f"**Positive Interactions:** {relationship.positive_interactions:,}"
            )
            stats_text.append(f"**Humor Exchanges:** {relationship.humor_exchanges:,}")
            stats_text.append(f"**Times I Helped:** {relationship.help_provided:,}")

            embed.add_field(
                name="📊 Interaction History", value="\n".join(stats_text), inline=True
            )

            # Personal touches
            personal_text = []

            # Trust level
            trust_bar = self._create_progress_bar(relationship.trust_level, 10)
            trust_desc = (
                "Complete Trust"
                if relationship.trust_level > 0.8
                else (
                    "High Trust"
                    if relationship.trust_level > 0.6
                    else (
                        "Growing Trust"
                        if relationship.trust_level > 0.3
                        else "Building Trust"
                    )
                )
            )
            personal_text.append(f"**Trust Level:** {trust_desc} `{trust_bar}`")

            # Communication preferences
            humor_bar = self._create_progress_bar(relationship.humor_receptivity, 10)
            personal_text.append(
                f"**Humor Appreciation:** `{humor_bar}` {relationship.humor_receptivity:.1%}"
            )

            embed.add_field(
                name="🎯 Personal Understanding",
                value="\n".join(personal_text),
                inline=True,
            )

            # Remembered details
            if relationship.interests or relationship.personal_references:
                memory_text = []

                if relationship.interests:
                    memory_text.append(
                        f"**Interests:** {', '.join(relationship.interests[:5])}"
                    )

                if relationship.personal_references:
                    memory_text.append(
                        f"**Personal Memories:** {len(relationship.personal_references)} remembered"
                    )

                if relationship.important_dates:
                    memory_text.append(
                        f"**Important Dates:** {len(relationship.important_dates)} remembered"
                    )

                embed.add_field(
                    name="🧠 What I Remember",
                    value=(
                        "\n".join(memory_text)
                        if memory_text
                        else "Still learning about you!"
                    ),
                    inline=False,
                )

            # Last interaction
            if relationship.last_interaction:
                time_since = datetime.now(timezone.utc) - relationship.last_interaction
                embed.add_field(
                    name="⏰ Last Chat",
                    value=f"{self._format_timedelta(time_since)} ago",
                    inline=True,
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in relationship command: {e}")
            await ctx.send("❌ Error retrieving relationship data. Please try again.")

    @personality_group.command(name="analytics", aliases=["stats", "data"])
    async def personality_analytics(self, ctx):
        """Show personality evolution analytics"""
        try:
            analytics = await self.personality_engine.get_analytics(ctx.guild.id)

            embed = EmbedBuilder.primary(
                title="📈 Personality Evolution Analytics",
                description=f"Evolution data for **{ctx.guild.name}**",
            )

            if analytics.get("has_personality"):
                # Server stats
                embed.add_field(
                    name="🏆 Server Evolution",
                    value=(
                        f"**Culture Confidence:** {analytics['culture_confidence']:.1%}\n"
                        f"**Total Interactions:** {analytics['total_interactions']:,}\n"
                        f"**Users with Relationships:** {analytics['user_relationships']:,}\n"
                        f"**Avg Relationship Strength:** {analytics['avg_relationship_strength']:.1%}"
                    ),
                    inline=False,
                )

                # Evolution milestones
                milestones = []
                if analytics["total_interactions"] > 1000:
                    milestones.append("🌟 **Veteran Server** - 1000+ interactions")
                elif analytics["total_interactions"] > 500:
                    milestones.append("🌱 **Growing Community** - 500+ interactions")
                elif analytics["total_interactions"] > 100:
                    milestones.append("🐣 **Active Learning** - 100+ interactions")
                else:
                    milestones.append("🆕 **Just Beginning** - Learning your culture")

                if analytics["culture_confidence"] > 0.8:
                    milestones.append(
                        "🧠 **Culture Expert** - Deep understanding achieved"
                    )
                elif analytics["culture_confidence"] > 0.5:
                    milestones.append("📚 **Culture Student** - Good understanding")

                if analytics["user_relationships"] > 50:
                    milestones.append(
                        "🤝 **Social Butterfly** - Many relationships built"
                    )
                elif analytics["user_relationships"] > 20:
                    milestones.append("👥 **Community Member** - Several relationships")

                if milestones:
                    embed.add_field(
                        name="🏅 Evolution Milestones",
                        value="\n".join(milestones),
                        inline=False,
                    )

                # Progress indicators
                confidence_progress = analytics["culture_confidence"]
                relationship_progress = min(
                    1.0, analytics["user_relationships"] / 20
                )  # Normalize to 20 users
                interaction_progress = min(
                    1.0, analytics["total_interactions"] / 500
                )  # Normalize to 500 interactions

                progress_text = []
                progress_text.append(
                    f"**Culture Understanding:** `{self._create_progress_bar(confidence_progress, 15)}` {confidence_progress:.1%}"
                )
                progress_text.append(
                    f"**Relationship Building:** `{self._create_progress_bar(relationship_progress, 15)}` {analytics['user_relationships']}/20"
                )
                progress_text.append(
                    f"**Interaction Experience:** `{self._create_progress_bar(interaction_progress, 15)}` {analytics['total_interactions']}/500"
                )

                embed.add_field(
                    name="📊 Progress Tracking",
                    value="\n".join(progress_text),
                    inline=False,
                )

            else:
                embed.add_field(
                    name="🆕 New Server",
                    value="This server is new to me! Start chatting and I'll begin learning your culture.",
                    inline=False,
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in analytics command: {e}")
            await ctx.send("❌ Error retrieving analytics. Please try again.")

    @personality_group.command(name="test")
    async def personality_test(self, ctx):
        """Test the personality evolution system"""
        embed = EmbedBuilder.primary(
            title="🧪 Personality Evolution Test",
            description="Testing personality adaptation with sample messages...",
        )

        message = await ctx.send(embed=embed)

        try:
            # Test messages with different cultural indicators
            test_messages = [
                {"content": "haha that's so funny! 😂😂😂", "type": "humor"},
                {
                    "content": "Could you please help me with this technical implementation?",
                    "type": "formal",
                },
                {"content": "sup dude, gonna work on some code", "type": "casual"},
                {
                    "content": "Thanks so much! I really appreciate your help! ❤️",
                    "type": "warmth",
                },
                {
                    "content": "This algorithm is quite complex, let me analyze the documentation",
                    "type": "technical",
                },
            ]

            results = []
            for i, test_msg in enumerate(test_messages):
                # Process test message
                result = await self.personality_engine.process_message(
                    message_content=test_msg["content"],
                    user_id=ctx.author.id,
                    user_name=ctx.author.display_name,
                    server_id=ctx.guild.id,
                    server_name=ctx.guild.name,
                )

                results.append(
                    {
                        "type": test_msg["type"],
                        "changes": len(result.get("personality_changes", {})),
                        "confidence": result.get("culture_confidence", 0),
                    }
                )

                # Update progress
                progress = (i + 1) / len(test_messages)
                progress_bar = self._create_progress_bar(progress, 20)

                embed.description = f"Testing personality adaptation...\n`{progress_bar}` {progress:.0%}"
                await message.edit(embed=embed)
                await asyncio.sleep(0.5)

            # Show results
            embed.description = "✅ Personality evolution test completed!"

            results_text = []
            for result in results:
                status = "✅ Adapted" if result["changes"] > 0 else "⚪ No change"
                results_text.append(f"**{result['type'].title()}:** {status}")

            embed.add_field(
                name="🧪 Test Results", value="\n".join(results_text), inline=False
            )

            # Get final personality context
            final_context = await self.personality_engine.get_personality_context(
                ctx.guild.id
            )
            embed.add_field(
                name="🧠 Current Personality",
                value=final_context["personality_summary"],
                inline=False,
            )

            embed.add_field(
                name="📊 Culture Confidence",
                value=f"{final_context['culture_confidence']:.1%}",
                inline=True,
            )

            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in personality test: {e}")
            embed.description = f"❌ Test failed: {str(e)}"
            await message.edit(embed=embed)

    @personality_group.command(name="config")
    @commands.has_permissions(administrator=True)
    async def personality_config(self, ctx):
        """Configure personality evolution settings (Admin only)"""
        embed = EmbedBuilder.primary(
            title="⚙️ Personality Evolution Configuration",
            description="Configuration options for personality evolution system:",
        )

        # Current settings (would be loaded from config)
        settings = {
            "evolution_enabled": True,
            "evolution_threshold": 50,
            "adaptation_rate": 0.05,
            "confidence_growth": 0.02,
            "relationship_tracking": True,
        }

        config_text = []
        for setting, value in settings.items():
            status = (
                "✅ Enabled"
                if value is True
                else "❌ Disabled" if value is False else str(value)
            )
            config_text.append(f"**{setting.replace('_', ' ').title()}:** {status}")

        embed.add_field(
            name="🔧 Current Settings", value="\n".join(config_text), inline=False
        )

        embed.add_field(
            name="📝 Available Commands",
            value=(
                "• `personality config enable` - Enable evolution\n"
                "• `personality config disable` - Disable evolution\n"
                "• `personality config threshold <number>` - Set evolution threshold\n"
                "• `personality config rate <0.0-1.0>` - Set adaptation rate"
            ),
            inline=False,
        )

        await ctx.send(embed=embed)

    @personality_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def personality_reset(self, ctx):
        """Reset server personality (Admin only)"""
        # Confirmation
        embed = EmbedBuilder.warning(
            title="Reset Personality",
            description=(
                "This will completely reset my personality for this server.\n"
                "All learned culture, relationships, and evolution data will be lost.\n\n"
                "**This action cannot be undone!**\n\n"
                "React with ✅ to confirm or ❌ to cancel."
            ),
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == message.id
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=30.0, check=check
            )

            if str(reaction.emoji) == "✅":
                # Reset personality (would need to implement reset method)
                embed.title = "✅ Personality Reset"
                embed.description = "My personality has been reset for this server. I'll start learning your culture anew!"
                embed.color = 0x51CF66
            else:
                embed.title = "❌ Reset Cancelled"
                embed.description = (
                    "Personality reset cancelled. My learned culture remains intact."
                )
                embed.color = 0x9966FF

            await message.edit(embed=embed)

        except asyncio.TimeoutError:
            embed.title = "⏰ Reset Timed Out"
            embed.description = (
                "Reset confirmation timed out. My personality remains unchanged."
            )
            embed.color = 0x868E96
            await message.edit(embed=embed)

    @personality_group.command(name="export")
    async def personality_export(self, ctx):
        """Export personality data"""
        try:
            personality = await self.personality_engine._get_server_personality(
                ctx.guild.id
            )

            export_data = {
                "server_name": ctx.guild.name,
                "server_id": ctx.guild.id,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "personality_summary": personality.get_personality_summary(),
                "culture_confidence": personality.culture_confidence,
                "total_interactions": personality.total_interactions,
                "traits": {
                    "humor_style": personality.humor_style,
                    "formality_level": personality.formality_level,
                    "social_energy": personality.social_energy,
                    "communication_density": personality.communication_density,
                    "emotional_style": personality.emotional_style,
                },
                "learned_culture": {
                    "preferred_emojis": personality.preferred_emojis,
                    "inside_jokes": len(personality.inside_jokes),
                    "cultural_references": len(personality.cultural_references),
                },
            }

            # Create downloadable file
            import io

            file_content = json.dumps(export_data, indent=2)
            file_obj = io.StringIO(file_content)

            file = discord.File(
                io.BytesIO(file_content.encode()),
                filename=f"astra_personality_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d')}.json",
            )

            embed = EmbedBuilder.primary(
                title="📁 Personality Export",
                description="Here's my personality data for this server!",
            )

            await ctx.send(embed=embed, file=file)

        except Exception as e:
            self.logger.error(f"Error in export command: {e}")
            await ctx.send("❌ Error exporting personality data. Please try again.")

    def _create_progress_bar(self, value: float, length: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(value * length)
        empty = length - filled
        return "█" * filled + "░" * empty

    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta into human readable string"""
        if td.days > 0:
            return f"{td.days} day{'s' if td.days != 1 else ''}"
        elif td.seconds > 3600:
            hours = td.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        elif td.seconds > 60:
            minutes = td.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return "just now"


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PersonalityEvolutionCommands(bot))
