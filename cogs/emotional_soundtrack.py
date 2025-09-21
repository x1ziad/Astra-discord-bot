"""
Emotional Soundtrack Commands
Commands for controlling the emotional soundtrack system
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ai.emotional_soundtrack import (
    get_emotional_soundtrack,
    MoodType,
    MusicGenre,
    TrackSource,
)
from ui.embeds import EmbedBuilder


class EmotionalSoundtrackCommands(commands.Cog):
    """Commands for emotional soundtrack system"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.soundtrack_commands")

        # Initialize emotional soundtrack system
        self.soundtrack = get_emotional_soundtrack()

        self.logger.info("Emotional Soundtrack Commands cog loaded")

    @commands.group(name="soundtrack", aliases=["music", "mood"])
    async def soundtrack_group(self, ctx):
        """Emotional soundtrack commands"""
        if ctx.invoked_subcommand is None:
            embed = EmbedBuilder.primary(
                title="🎵 Emotional Soundtrack System",
                description=(
                    "Experience music that adapts to your community's emotional state!\n\n"
                    "**🎯 Available Commands:**\n"
                    "• `soundtrack start` - Start an emotional soundtrack session\n"
                    "• `soundtrack stop` - Stop the current session\n"
                    "• `soundtrack mood <mood>` - Set the current mood\n"
                    "• `soundtrack skip` - Skip to the next track\n"
                    "• `soundtrack volume <0-100>` - Adjust volume\n"
                    "• `soundtrack add <url>` - Add a music track\n"
                    "• `soundtrack library` - View music library\n"
                    "• `soundtrack stats` - View listening statistics\n\n"
                    "**🎭 Available Moods:** joyful, calm, energetic, melancholic, angry, peaceful, excited, reflective, romantic, mysterious\n\n"
                    "**✨ How It Works:**\n"
                    "→ Analyzes conversation mood in real-time\n"
                    "→ Automatically selects music that matches the emotional atmosphere\n"
                    "→ Creates immersive experiences that enhance community connection\n"
                    "→ Learns from your community's musical preferences"
                ),
            )
            embed.add_field(
                name="🎶 Adaptive Music",
                value="Music that feels the room and responds accordingly!",
                inline=True,
            )
            embed.add_field(
                name="🌊 Emotional Journey",
                value="From calm reflection to energetic celebration.",
                inline=True,
            )
            embed.add_field(
                name="🤝 Community Bonding",
                value="Shared musical experiences strengthen connections.",
                inline=True,
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="start", aliases=["begin", "play"])
    async def start_soundtrack(self, ctx, mood: str = None, auto_mode: str = "auto"):
        """Start an emotional soundtrack session"""
        try:
            # Check if user is in a voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = EmbedBuilder.error(
                    title="❌ Not in Voice Channel",
                    description="You must be in a voice channel to start a soundtrack session.\n\n**Please join a voice channel first!**",
                )
                await ctx.send(embed=embed)
                return

            voice_channel = ctx.author.voice.channel

            # Check if session already exists
            if voice_channel.id in self.soundtrack.active_sessions:
                embed = EmbedBuilder.info(
                    title="ℹ️ Session Already Active",
                    description=f"A soundtrack session is already running in **{voice_channel.name}**.\n\n**Use `soundtrack stop` to end it, or join the channel to participate!**",
                )
                await ctx.send(embed=embed)
                return

            # Parse mood
            initial_mood = MoodType.CALM
            if mood:
                try:
                    initial_mood = MoodType(mood.lower())
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Mood",
                        description=f"'{mood}' is not a valid mood. Available moods: {', '.join([m.value for m in MoodType])}",
                    )
                    await ctx.send(embed=embed)
                    return

            # Parse auto mode
            auto_enabled = auto_mode.lower() in ["auto", "automatic", "true", "yes"]

            # Start session
            session = await self.soundtrack.start_soundtrack_session(
                server_id=ctx.guild.id,
                channel_id=voice_channel.id,
                started_by=ctx.author.id,
                initial_mood=initial_mood,
                auto_mode=auto_enabled,
            )

            embed = EmbedBuilder.success(
                title="🎵 Soundtrack Session Started!",
                description=f"Started an emotional soundtrack session in **{voice_channel.name}**!",
            )

            embed.add_field(
                name="🎭 Initial Mood",
                value=initial_mood.value.title(),
                inline=True,
            )

            embed.add_field(
                name="🤖 Auto Mode",
                value=(
                    "Enabled (adapts to conversation)"
                    if auto_enabled
                    else "Disabled (manual control)"
                ),
                inline=True,
            )

            embed.add_field(
                name="🔊 Voice Channel",
                value=voice_channel.name,
                inline=True,
            )

            embed.add_field(
                name="🎶 Next Steps",
                value="• The system will analyze conversation mood\n"
                "• Music will adapt to match the emotional atmosphere\n"
                "• Use `soundtrack mood <mood>` to manually change mood\n"
                "• Use `soundtrack skip` to skip tracks\n"
                "• Use `soundtrack stop` to end the session",
                inline=False,
            )

            embed.set_footer(
                text=f"Session started by {ctx.author.display_name} | Use 'soundtrack help' for more commands"
            )
            await ctx.send(embed=embed)

            # Try to play first track
            track = await self.soundtrack.play_next_track(voice_channel.id)
            if track:
                await ctx.send(f"🎵 Now playing: **{track.title}** by *{track.artist}*")
            else:
                await ctx.send(
                    "⚠️ No suitable tracks found. Add some music with `soundtrack add <url>`!"
                )

        except Exception as e:
            self.logger.error(f"Error starting soundtrack: {e}")
            embed = EmbedBuilder.error(
                title="❌ Session Start Failed",
                description=f"Unable to start soundtrack session: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="stop", aliases=["end", "quit"])
    async def stop_soundtrack(self, ctx):
        """Stop the current soundtrack session"""
        try:
            # Find user's voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = EmbedBuilder.error(
                    title="❌ Not in Voice Channel",
                    description="You must be in a voice channel with an active session to stop it.",
                )
                await ctx.send(embed=embed)
                return

            voice_channel = ctx.author.voice.channel

            # Check if session exists
            if voice_channel.id not in self.soundtrack.active_sessions:
                embed = EmbedBuilder.info(
                    title="ℹ️ No Active Session",
                    description=f"No soundtrack session is running in **{voice_channel.name}**.",
                )
                await ctx.send(embed=embed)
                return

            session = self.soundtrack.active_sessions[voice_channel.id]

            # Check permissions (session starter or admin)
            if (
                ctx.author.id != session.started_by
                and not ctx.author.guild_permissions.administrator
            ):
                embed = EmbedBuilder.error(
                    title="❌ Permission Denied",
                    description="Only the session starter or administrators can stop the soundtrack.",
                )
                await ctx.send(embed=embed)
                return

            # Stop session
            success = await self.soundtrack.stop_session(voice_channel.id)

            if success:
                embed = EmbedBuilder.success(
                    title="🛑 Soundtrack Session Ended",
                    description=f"Stopped the emotional soundtrack session in **{voice_channel.name}**.",
                )

                embed.add_field(
                    name="⏱️ Session Duration",
                    value=f"Running for {(datetime.now(timezone.utc) - session.started_at).total_seconds() / 60:.1f} minutes",
                    inline=True,
                )

                embed.add_field(
                    name="🎵 Tracks Played",
                    value=f"{len(session.mood_history)} mood adaptations",
                    inline=True,
                )

                embed.set_footer(text=f"Session ended by {ctx.author.display_name}")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Stop Failed",
                    description="Unable to stop the soundtrack session.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error stopping soundtrack: {e}")
            embed = EmbedBuilder.error(
                title="❌ Stop Error",
                description=f"Unable to stop soundtrack: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="mood", aliases=["setmood", "emotion"])
    async def set_mood(self, ctx, mood: str):
        """Set the current mood for the soundtrack"""
        try:
            # Find user's voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = EmbedBuilder.error(
                    title="❌ Not in Voice Channel",
                    description="You must be in a voice channel with an active session.",
                )
                await ctx.send(embed=embed)
                return

            voice_channel = ctx.author.voice.channel

            # Check if session exists
            if voice_channel.id not in self.soundtrack.active_sessions:
                embed = EmbedBuilder.info(
                    title="ℹ️ No Active Session",
                    description=f"No soundtrack session is running in **{voice_channel.name}**.",
                )
                await ctx.send(embed=embed)
                return

            # Validate mood
            try:
                new_mood = MoodType(mood.lower())
            except ValueError:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Mood",
                    description=f"'{mood}' is not a valid mood. Available moods: {', '.join([m.value for m in MoodType])}",
                )
                await ctx.send(embed=embed)
                return

            # Update mood
            success = await self.soundtrack.update_session_mood(
                voice_channel.id, new_mood
            )

            if success:
                embed = EmbedBuilder.success(
                    title=f"🎭 Mood Changed to {new_mood.value.title()}",
                    description=f"Updated the soundtrack mood in **{voice_channel.name}**!",
                )

                # Try to play a new track for the mood
                track = await self.soundtrack.play_next_track(voice_channel.id)
                if track:
                    embed.add_field(
                        name="🎵 Now Playing",
                        value=f"**{track.title}** by *{track.artist}*",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="⚠️ No Suitable Tracks",
                        value="No tracks found for this mood. Add more music with `soundtrack add`!",
                        inline=False,
                    )

                embed.set_footer(text=f"Mood changed by {ctx.author.display_name}")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Mood Change Failed",
                    description="Unable to change the soundtrack mood.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error setting mood: {e}")
            embed = EmbedBuilder.error(
                title="❌ Mood Error",
                description=f"Unable to set mood: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="skip", aliases=["next", "change"])
    async def skip_track(self, ctx):
        """Skip to the next track"""
        try:
            # Find user's voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = EmbedBuilder.error(
                    title="❌ Not in Voice Channel",
                    description="You must be in a voice channel with an active session.",
                )
                await ctx.send(embed=embed)
                return

            voice_channel = ctx.author.voice.channel

            # Check if session exists
            if voice_channel.id not in self.soundtrack.active_sessions:
                embed = EmbedBuilder.info(
                    title="ℹ️ No Active Session",
                    description=f"No soundtrack session is running in **{voice_channel.name}**.",
                )
                await ctx.send(embed=embed)
                return

            # Play next track
            track = await self.soundtrack.play_next_track(voice_channel.id)

            if track:
                embed = EmbedBuilder.success(
                    title="⏭️ Track Skipped",
                    description=f"Playing the next track in **{voice_channel.name}**!",
                )

                embed.add_field(
                    name="🎵 Now Playing",
                    value=f"**{track.title}** by *{track.artist}*",
                    inline=True,
                )

                embed.add_field(
                    name="🎭 Current Mood",
                    value=self.soundtrack.active_sessions[
                        voice_channel.id
                    ].current_mood.value.title(),
                    inline=True,
                )

                embed.add_field(
                    name="⏱️ Duration",
                    value=f"{track.duration // 60}:{track.duration % 60:02d}",
                    inline=True,
                )

                embed.set_footer(text=f"Skipped by {ctx.author.display_name}")
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.warning(
                    title="⚠️ No Tracks Available",
                    description="No suitable tracks found for the current mood.\n\n**Add more music with `soundtrack add <url>`!**",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error skipping track: {e}")
            embed = EmbedBuilder.error(
                title="❌ Skip Error",
                description=f"Unable to skip track: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="volume", aliases=["vol", "loudness"])
    async def set_volume(self, ctx, volume: int):
        """Set the soundtrack volume (0-100)"""
        try:
            # Validate volume
            if not 0 <= volume <= 100:
                embed = EmbedBuilder.error(
                    title="❌ Invalid Volume",
                    description="Volume must be between 0 and 100.",
                )
                await ctx.send(embed=embed)
                return

            # Find user's voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = EmbedBuilder.error(
                    title="❌ Not in Voice Channel",
                    description="You must be in a voice channel with an active session.",
                )
                await ctx.send(embed=embed)
                return

            voice_channel = ctx.author.voice.channel

            # Check if session exists
            if voice_channel.id not in self.soundtrack.active_sessions:
                embed = EmbedBuilder.info(
                    title="ℹ️ No Active Session",
                    description=f"No soundtrack session is running in **{voice_channel.name}**.",
                )
                await ctx.send(embed=embed)
                return

            session = self.soundtrack.active_sessions[voice_channel.id]
            session.volume = volume / 100.0  # Convert to 0.0-1.0

            embed = EmbedBuilder.success(
                title="🔊 Volume Adjusted",
                description=f"Set soundtrack volume to **{volume}%** in **{voice_channel.name}**!",
            )

            embed.add_field(
                name="🎵 Current Track",
                value=(
                    f"**{session.current_track.title}** by *{session.current_track.artist}*"
                    if session.current_track
                    else "No track playing"
                ),
                inline=False,
            )

            embed.set_footer(text=f"Volume adjusted by {ctx.author.display_name}")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            embed = EmbedBuilder.error(
                title="❌ Volume Error",
                description=f"Unable to set volume: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="add", aliases=["upload", "track"])
    async def add_track(
        self, ctx, url: str, title: str = None, artist: str = None, mood: str = None
    ):
        """Add a music track to the library"""
        try:
            # Basic URL validation
            if not url.startswith(("http://", "https://")):
                embed = EmbedBuilder.error(
                    title="❌ Invalid URL",
                    description="Please provide a valid HTTP/HTTPS URL for the music track.",
                )
                await ctx.send(embed=embed)
                return

            # If title/artist not provided, try to extract from URL or use defaults
            if not title:
                title = f"Track from {url.split('/')[-1][:50]}"
            if not artist:
                artist = "Unknown Artist"

            # Parse mood if provided
            mood_associations = {}
            if mood:
                try:
                    mood_type = MoodType(mood.lower())
                    mood_associations[mood_type] = (
                        0.8  # High confidence for user-specified mood
                    )
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Mood",
                        description=f"'{mood}' is not a valid mood. Available moods: {', '.join([m.value for m in MoodType])}",
                    )
                    await ctx.send(embed=embed)
                    return

            # Determine source
            if "youtube.com" in url or "youtu.be" in url:
                source = TrackSource.YOUTUBE
            elif "spotify.com" in url:
                source = TrackSource.SPOTIFY
            elif "soundcloud.com" in url:
                source = TrackSource.SOUNDCLOUD
            else:
                source = TrackSource.URL

            # Add track (duration will be estimated or updated later)
            track = await self.soundtrack.add_track(
                title=title,
                artist=artist,
                source=source,
                source_url=url,
                duration=180,  # Default 3 minutes, can be updated
                added_by=ctx.author.id,
                mood_associations=mood_associations,
            )

            if track:
                embed = EmbedBuilder.success(
                    title="🎵 Track Added!",
                    description=f"Successfully added **{track.title}** by *{track.artist}* to the music library!",
                )

                embed.add_field(
                    name="🔗 Source",
                    value=f"[{source.value.title()}]({url})",
                    inline=True,
                )

                embed.add_field(
                    name="🎭 Associated Mood",
                    value=mood.title() if mood else "Auto-detected",
                    inline=True,
                )

                embed.add_field(
                    name="👤 Added By",
                    value=ctx.author.mention,
                    inline=True,
                )

                embed.add_field(
                    name="💡 Pro Tip",
                    value="The system will analyze this track and associate it with appropriate moods for better emotional matching!",
                    inline=False,
                )

                embed.set_footer(
                    text=f"Track ID: {track.id} | Added to emotional soundtrack library"
                )
                await ctx.send(embed=embed)
            else:
                embed = EmbedBuilder.error(
                    title="❌ Track Addition Failed",
                    description="Unable to add the track to the library.",
                )
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error adding track: {e}")
            embed = EmbedBuilder.error(
                title="❌ Track Error",
                description=f"Unable to add track: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="library", aliases=["tracks", "songs"])
    async def view_library(self, ctx, mood: str = None, limit: int = 10):
        """View the music library"""
        try:
            if mood:
                # Validate mood
                try:
                    mood_type = MoodType(mood.lower())
                    tracks = await self.soundtrack.get_tracks_for_mood(
                        mood_type, limit=limit
                    )
                    title_suffix = f" for {mood_type.value.title()} Mood"
                except ValueError:
                    embed = EmbedBuilder.error(
                        title="❌ Invalid Mood",
                        description=f"'{mood}' is not a valid mood. Available moods: {', '.join([m.value for m in MoodType])}",
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                tracks = await self.soundtrack.get_all_tracks()
                title_suffix = ""

            if not tracks:
                embed = EmbedBuilder.info(
                    title=f"🎵 Music Library{title_suffix}",
                    description="No tracks found in the library.\n\n**Add some music with:** `soundtrack add <url> <title> <artist>`",
                )
                await ctx.send(embed=embed)
                return

            embed = EmbedBuilder.primary(
                title=f"🎵 Music Library{title_suffix} ({len(tracks)} tracks)",
                description="Your community's emotional soundtrack collection!",
            )

            for track in tracks[:10]:  # Show up to 10 tracks
                best_mood, mood_score = track.get_best_mood_match()

                embed.add_field(
                    name=f"🎶 {track.title}",
                    value=f"**Artist:** {track.artist}\n"
                    f"**Genre:** {track.genre.value.title()}\n"
                    f"**Best Mood:** {best_mood.value.title()} ({mood_score:.1f})\n"
                    f"**Plays:** {track.play_count}\n"
                    f"**Duration:** {track.duration // 60}:{track.duration % 60:02d}",
                    inline=True,
                )

            if len(tracks) > 10:
                embed.add_field(
                    name="📄 More Tracks",
                    value=f"There are {len(tracks) - 10} more tracks. Use `soundtrack library <mood>` to filter by mood!",
                    inline=False,
                )

            embed.set_footer(
                text=f"Total tracks: {len(tracks)} | Use 'soundtrack add' to contribute more music!"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error viewing library: {e}")
            embed = EmbedBuilder.error(
                title="❌ Library Error",
                description=f"Unable to load music library: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="stats", aliases=["statistics", "info"])
    async def soundtrack_stats(self, ctx):
        """View soundtrack statistics"""
        try:
            stats = await self.soundtrack.get_session_stats(ctx.guild.id)

            embed = EmbedBuilder.primary(
                title="📊 Emotional Soundtrack Statistics",
                description="How your community experiences music and emotion together!",
            )

            embed.add_field(
                name="🎵 Music Library",
                value=f"**Total Tracks:** {stats['total_tracks']}\n"
                f"**Active Sessions:** {stats['active_sessions']}\n"
                f"**Total Plays:** {stats['total_plays']:,}",
                inline=True,
            )

            if stats.get("mood_play_counts"):
                mood_plays = stats["mood_play_counts"]
                top_moods = sorted(
                    mood_plays.items(), key=lambda x: x[1], reverse=True
                )[:5]

                mood_stats = "\n".join(
                    [f"• {mood.title()}: {count}" for mood, count in top_moods]
                )
                embed.add_field(
                    name="🎭 Most Played Moods",
                    value=mood_stats,
                    inline=True,
                )

            embed.add_field(
                name="📈 Community Insights",
                value=f"**Most Played Mood:** {stats.get('most_played_mood', 'None yet')}\n"
                f"**Avg Tracks/Mood:** {stats.get('average_tracks_per_mood', 0):.1f}\n"
                f"**Emotional Range:** {len(stats.get('mood_play_counts', {}))} moods explored",
                inline=True,
            )

            embed.add_field(
                name="🌟 Emotional Intelligence",
                value="• Music adapts to conversation mood in real-time\n"
                "• Community preferences shape the emotional experience\n"
                "• Shared musical journeys strengthen bonds\n"
                "• AI learns what music resonates with your community",
                inline=False,
            )

            embed.set_footer(
                text=f"Server: {ctx.guild.name} | Keep creating emotional musical experiences!"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error getting soundtrack stats: {e}")
            embed = EmbedBuilder.error(
                title="❌ Statistics Error",
                description=f"Unable to load statistics: {str(e)}",
            )
            await ctx.send(embed=embed)

    @soundtrack_group.command(name="analyze", aliases=["moodcheck"])
    async def analyze_mood(self, ctx, channel: discord.TextChannel = None):
        """Analyze the current mood of a channel"""
        try:
            target_channel = channel or ctx.channel

            # Get recent messages (last 50)
            messages = []
            async for message in target_channel.history(limit=50):
                if not message.author.bot:
                    messages.append(
                        {
                            "content": message.content,
                            "author_id": message.author.id,
                            "timestamp": message.created_at.isoformat(),
                        }
                    )

            if not messages:
                embed = EmbedBuilder.info(
                    title="📭 No Messages Found",
                    description=f"No recent messages found in {target_channel.mention} to analyze.",
                )
                await ctx.send(embed=embed)
                return

            # Analyze mood
            mood_snapshot = await self.soundtrack.analyze_conversation_mood(
                server_id=ctx.guild.id,
                channel_id=target_channel.id,
                messages=messages,
            )

            dominant_mood, mood_score = mood_snapshot.get_dominant_mood()

            embed = EmbedBuilder.primary(
                title=f"🎭 Mood Analysis: {target_channel.name}",
                description=f"Analyzed the emotional atmosphere of recent conversations!",
            )

            embed.add_field(
                name="🎯 Dominant Mood",
                value=f"**{dominant_mood.value.title()}** ({mood_score:.2f})",
                inline=True,
            )

            embed.add_field(
                name="📊 Sentiment Score",
                value=f"{mood_snapshot.sentiment_score:.2f} (-1.0 to 1.0)",
                inline=True,
            )

            embed.add_field(
                name="👥 Active Users",
                value=f"{mood_snapshot.active_users} contributors",
                inline=True,
            )

            # Show top mood scores
            top_moods = sorted(
                mood_snapshot.mood_scores.items(), key=lambda x: x[1], reverse=True
            )[:5]
            mood_breakdown = "\n".join(
                [f"• {mood.value.title()}: {score:.2f}" for mood, score in top_moods]
            )

            embed.add_field(
                name="📈 Mood Breakdown",
                value=mood_breakdown,
                inline=False,
            )

            if mood_snapshot.conversation_topics:
                topics_str = ", ".join(mood_snapshot.conversation_topics[:5])
                embed.add_field(
                    name="💬 Conversation Topics",
                    value=topics_str,
                    inline=False,
                )

            embed.set_footer(
                text=f"Analysis based on {mood_snapshot.message_count} recent messages"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error analyzing mood: {e}")
            embed = EmbedBuilder.error(
                title="❌ Analysis Error",
                description=f"Unable to analyze mood: {str(e)}",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(EmotionalSoundtrackCommands(bot))
