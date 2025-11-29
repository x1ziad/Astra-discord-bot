"""
🔊 AI-Powered Announcement System for Astra
Advanced announcement management with AI analysis and Q&A

Features:
- AI-powered announcement creation and formatting
- Smart content analysis and key point extraction
- Interactive Q&A about announcements
- Multiple delivery modes (public/DM/both)
- Announcement history and analytics
- Follow-up question handling

Author: x1ziad
Version: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import discord
from discord.ext import commands, tasks
from discord import app_commands

from utils.database import db
from config.unified_config import unified_config


@dataclass
class AnnouncementData:
    """Data structure for announcements"""

    announcement_id: str
    title: str
    content: str
    author_id: int
    guild_id: int
    created_at: str
    delivery_mode: str  # "public", "dm", "both"
    channel_id: Optional[int] = None

    # AI-enhanced fields
    key_points: List[str] = field(default_factory=list)
    summary: str = ""
    faq: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Analytics
    views: int = 0
    reactions: Dict[str, int] = field(default_factory=dict)
    questions_asked: int = 0
    dm_sent: int = 0
    dm_failed: int = 0


class AIAnnouncements(commands.Cog):
    """AI-powered announcement system for Astra"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.ai_announcements")
        self.db = db

        # AI client (will be set dynamically)
        self.ai_client = None

        # Default channel IDs
        self.ANNOUNCEMENTS_CHANNEL_ID = 1399956513745014971  # General announcements
        self.MOD_UPDATES_CHANNEL_ID = 1400021413934534766  # Moderation/admin updates

        # Announcement cache
        self.announcements: Dict[str, AnnouncementData] = {}
        self.guild_announcements: Dict[int, List[str]] = {}

        # Question tracking for context
        self.announcement_questions: Dict[str, List[Dict]] = {}

        # Rate limiting for DM sending
        self.dm_queue: Dict[int, List[Tuple]] = {}
        self.dm_rate_limit = 1.0  # Seconds between DMs

        # Initialize database
        self._init_database()

        # Start background tasks
        self.process_dm_queue_task.start()
        self.cleanup_old_data_task.start()

        self.logger.info("✅ AI Announcements system initialized")

    def _init_database(self):
        """Initialize announcement database tables"""
        try:
            # Announcements table
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS announcements (
                    announcement_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    delivery_mode TEXT NOT NULL,
                    channel_id INTEGER,
                    key_points TEXT,
                    summary TEXT,
                    faq TEXT,
                    tags TEXT,
                    views INTEGER DEFAULT 0,
                    reactions TEXT,
                    questions_asked INTEGER DEFAULT 0,
                    dm_sent INTEGER DEFAULT 0,
                    dm_failed INTEGER DEFAULT 0
                )
            """
            )

            # Announcement questions table (for Q&A history)
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS announcement_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    announcement_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    asked_at TEXT NOT NULL,
                    FOREIGN KEY (announcement_id) REFERENCES announcements (announcement_id)
                )
            """
            )

            # Create indexes for performance
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_announcements_guild ON announcements(guild_id, created_at DESC)"
            )
            self.db.execute(
                "CREATE INDEX IF NOT EXISTS idx_questions_announcement ON announcement_questions(announcement_id, asked_at DESC)"
            )

            self.logger.info("✅ Announcement database initialized with indexes")
        except Exception as e:
            self.logger.error(f"Error initializing announcement database: {e}")

    def _get_ai_client(self):
        """Get AI client dynamically"""
        if not self.ai_client:
            self.ai_client = getattr(self.bot, "ai_manager", None)
        return self.ai_client

    async def _generate_with_ai(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using AI with error handling and fallback"""
        try:
            ai = self._get_ai_client()
            if not ai:
                self.logger.warning("AI client not available")
                return ""

            # Try to generate response with timeout
            response = await asyncio.wait_for(
                ai.generate_response(
                    prompt=prompt, max_tokens=max_tokens, temperature=0.7
                ),
                timeout=30.0,  # 30 second timeout
            )

            if response:
                # Handle both string and AIResponse object
                if hasattr(response, 'content'):
                    return response.content.strip() if response.content else ""
                elif isinstance(response, str):
                    return response.strip()
                else:
                    return str(response).strip()

            self.logger.warning("AI returned empty response")
            return ""

        except asyncio.TimeoutError:
            self.logger.error("AI generation timed out after 30 seconds")
            return ""
        except AttributeError as e:
            self.logger.error(f"AI client missing generate_response method: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"AI generation error: {e}")
            return ""

    async def analyze_announcement_with_ai(
        self, title: str, content: str
    ) -> Dict[str, Any]:
        """Use AI to analyze announcement and extract key information with optimized prompt"""

        # Optimized prompt - clearer, more concise, better JSON structure
        analysis_prompt = f"""You are analyzing a Discord server announcement. Extract key information and format as valid JSON.

ANNOUNCEMENT:
Title: {title}
Content: {content}

REQUIRED OUTPUT (valid JSON only, no markdown):
{{
    "key_points": ["3-5 concise bullet points of critical information"],
    "summary": "1-2 sentence overview capturing the essence",
    "faq": [
        {{"q": "Common question 1?", "a": "Clear answer based on content"}},
        {{"q": "Common question 2?", "a": "Clear answer based on content"}},
        {{"q": "Common question 3?", "a": "Clear answer based on content"}}
    ],
    "tags": ["3-5 relevant keywords"]
}}

Return ONLY valid JSON. No explanation, no markdown formatting."""

        try:
            response = await self._generate_with_ai(analysis_prompt, max_tokens=1500)

            # Try to parse JSON response
            if response:
                # Extract JSON if wrapped in markdown
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                analysis = json.loads(response)
                return analysis

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse AI JSON response: {e}")
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")

        # Fallback: basic analysis
        return {
            "key_points": ["Check the full announcement for details"],
            "summary": f"Announcement: {title}",
            "faq": {},
            "tags": [],
        }

    async def answer_question_with_ai(
        self, announcement: AnnouncementData, question: str, user_name: str = "User"
    ) -> str:
        """Use AI to answer questions about the announcement with full context and stored details"""

        # Build comprehensive context with ALL announcement details
        faq_text = ""
        if announcement.faq:
            if isinstance(announcement.faq, dict):
                faq_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in list(announcement.faq.items())[:3]])
            elif isinstance(announcement.faq, list):
                faq_text = "\n".join([f"Q: {item.get('q', '')}\nA: {item.get('a', '')}" for item in announcement.faq[:3]])
        
        context_parts = [
            f"You are Astra, an intelligent AI assistant. A user is asking about this announcement:\n",
            f"TITLE: {announcement.title}\n",
            f"FULL CONTENT:\n{announcement.content}\n",
            f"\nKEY POINTS EXTRACTED:\n" + "\n".join(f"• {point}" for point in announcement.key_points) if announcement.key_points else "",
            f"\n\nSUMMARY: {announcement.summary}\n" if announcement.summary else "",
            f"\nFREQUENTLY ASKED:\n{faq_text}\n" if faq_text else "",
            f"\nTAGS: {', '.join(announcement.tags)}\n" if announcement.tags else "",
        ]

        # Add previous Q&A for continuity
        if announcement.announcement_id in self.announcement_questions:
            recent_qa = self.announcement_questions[announcement.announcement_id][-3:]
            if recent_qa:
                context_parts.append("\n\nPREVIOUS QUESTIONS ABOUT THIS ANNOUNCEMENT:")
                for qa in recent_qa:
                    context_parts.append(f"Q: {qa['question']}\nA: {qa['answer']}\n")

        # Enhanced prompt with all details
        qa_prompt = f"""{''.join(context_parts)}

NEW QUESTION from {user_name}: {question}

Provide a detailed, accurate answer based on ALL the announcement information above. Reference specific details like prices, dates, locations, requirements, or any other relevant information mentioned in the content. If the exact answer isn't explicitly stated, use the context to provide the most helpful response possible. Be conversational and friendly as Astra."""

        try:
            answer = await self._generate_with_ai(qa_prompt, max_tokens=1200)
            if answer:
                return answer
        except Exception as e:
            self.logger.error(f"Error generating answer: {e}")

        return f"I'm having trouble processing that question right now. Please check the full announcement titled '{announcement.title}' for details! 🤖"

    # ============================================================================
    # SLASH COMMANDS
    # ============================================================================

    @app_commands.command(name="announce")
    @app_commands.describe(
        title="Announcement title",
        content="Announcement content (use \\n for line breaks)",
        delivery="Where to send: public (channel), dm (private messages), or both",
        channel="Channel for public announcement (optional, defaults to current)",
    )
    @app_commands.choices(
        delivery=[
            app_commands.Choice(name="📢 Public (Channel Only)", value="public"),
            app_commands.Choice(name="📨 Private (DM Only)", value="dm"),
            app_commands.Choice(name="📢📨 Both (Channel + DM)", value="both"),
        ]
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        title: str,
        content: str,
        delivery: str = "public",
        channel: Optional[discord.TextChannel] = None,
    ):
        """🔊 Create an AI-powered announcement with smart analysis"""

        # Permission check
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need 'Manage Server' permission to create announcements.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Process content (handle \n for line breaks)
            content = content.replace("\\n", "\n")

            # Use specified channel, or default announcements channel, or current channel
            if channel:
                target_channel = channel
            else:
                # Try to get default announcements channel
                default_channel = interaction.guild.get_channel(
                    self.ANNOUNCEMENTS_CHANNEL_ID
                )
                target_channel = default_channel or interaction.channel

            # Generate unique ID
            announcement_id = (
                f"{interaction.guild_id}_{int(datetime.now().timestamp())}"
            )

            # AI analysis
            await interaction.followup.send(
                "🤖 Analyzing announcement with AI...", ephemeral=True
            )

            analysis = await self.analyze_announcement_with_ai(title, content)

            # Create announcement object
            announcement = AnnouncementData(
                announcement_id=announcement_id,
                title=title,
                content=content,
                author_id=interaction.user.id,
                guild_id=interaction.guild_id,
                created_at=datetime.now().isoformat(),
                delivery_mode=delivery,
                channel_id=(
                    target_channel.id if delivery in ["public", "both"] else None
                ),
                key_points=analysis.get("key_points", []),
                summary=analysis.get("summary", ""),
                faq=analysis.get("faq", {}),
                tags=analysis.get("tags", []),
            )

            # Save to database
            await self._save_announcement(announcement)

            # Cache announcement
            self.announcements[announcement_id] = announcement
            if interaction.guild_id not in self.guild_announcements:
                self.guild_announcements[interaction.guild_id] = []
            self.guild_announcements[interaction.guild_id].append(announcement_id)

            # Create announcement embed
            embed = self._create_announcement_embed(announcement, interaction.user)

            # Send based on delivery mode
            sent_messages = []

            if delivery in ["public", "both"]:
                # Send to channel
                try:
                    msg = await target_channel.send(embed=embed)
                    sent_messages.append(f"✅ Posted in {target_channel.mention}")

                    # Add reaction for questions
                    await msg.add_reaction("❓")
                    await msg.add_reaction("📌")
                except Exception as e:
                    self.logger.error(f"Error sending to channel: {e}")
                    sent_messages.append(
                        f"❌ Failed to post in {target_channel.mention}"
                    )

            if delivery in ["dm", "both"]:
                # Queue DMs to all members
                members = [m for m in interaction.guild.members if not m.bot]
                announcement.dm_sent = 0
                announcement.dm_failed = 0

                # Add to queue
                if interaction.guild_id not in self.dm_queue:
                    self.dm_queue[interaction.guild_id] = []

                for member in members:
                    self.dm_queue[interaction.guild_id].append(
                        (member, embed, announcement_id)
                    )

                sent_messages.append(
                    f"📬 Queued DMs for {len(members)} members (sending in background)"
                )

            # Show analysis
            analysis_embed = discord.Embed(
                title="📊 AI Analysis Complete",
                description=f"**Summary:** {announcement.summary}",
                color=discord.Color.green(),
            )

            if announcement.key_points:
                analysis_embed.add_field(
                    name="🎯 Key Points",
                    value="\n".join(
                        f"• {point}" for point in announcement.key_points[:5]
                    ),
                    inline=False,
                )

            if announcement.tags:
                analysis_embed.add_field(
                    name="🏷️ Tags",
                    value=", ".join(f"`{tag}`" for tag in announcement.tags[:5]),
                    inline=False,
                )

            analysis_embed.add_field(
                name="📤 Delivery Status", value="\n".join(sent_messages), inline=False
            )

            analysis_embed.add_field(
                name="💬 Q&A Feature",
                value=f"Use `/ask_announcement {announcement_id}` to answer questions!\nUsers can react with ❓ or use the command.",
                inline=False,
            )

            await interaction.followup.send(embed=analysis_embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error creating announcement: {e}")
            await interaction.followup.send(
                f"❌ Error creating announcement: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="ask_announcement")
    @app_commands.describe(
        announcement_id="The announcement ID (or use 'latest' for most recent)",
        question="Your question about the announcement",
    )
    async def ask_announcement(
        self, interaction: discord.Interaction, announcement_id: str, question: str
    ):
        """❓ Ask a question about an announcement - AI will answer!"""

        await interaction.response.defer(ephemeral=False)

        try:
            # Handle 'latest'
            if announcement_id.lower() == "latest":
                guild_announcements = self.guild_announcements.get(
                    interaction.guild_id, []
                )
                if not guild_announcements:
                    await interaction.followup.send(
                        "❌ No announcements found in this server.", ephemeral=True
                    )
                    return
                announcement_id = guild_announcements[-1]

            # Get announcement
            announcement = self.announcements.get(announcement_id)
            if not announcement:
                # Try loading from database
                announcement = self._load_announcement(announcement_id)

            if not announcement:
                await interaction.followup.send(
                    "❌ Announcement not found. Use `/list_announcements` to see available ones.",
                    ephemeral=True,
                )
                return

            # Generate AI answer
            answer = await self.answer_question_with_ai(
                announcement, question, interaction.user.display_name
            )

            # Save Q&A
            await self._save_question(announcement_id, interaction.user.id, question, answer)

            # Update stats
            announcement.questions_asked += 1
            await self._update_announcement_stats(announcement)

            # Create response embed
            embed = discord.Embed(
                title=f"💬 Q&A: {announcement.title}", color=discord.Color.blue()
            )

            embed.add_field(
                name=f"❓ {interaction.user.display_name} asked:",
                value=question,
                inline=False,
            )

            embed.add_field(name="🤖 Astra's Answer:", value=answer, inline=False)

            embed.set_footer(text=f"Announcement ID: {announcement_id}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
            await interaction.followup.send(
                f"❌ Error processing question: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="list_announcements")
    @app_commands.describe(limit="Number of recent announcements to show (default: 5)")
    async def list_announcements(
        self, interaction: discord.Interaction, limit: int = 5
    ):
        """📋 List recent announcements in this server"""

        guild_id = interaction.guild_id
        guild_announcements = self.guild_announcements.get(guild_id, [])

        if not guild_announcements:
            await interaction.response.send_message(
                "📭 No announcements have been created in this server yet.",
                ephemeral=True,
            )
            return

        # Get recent announcements
        recent = guild_announcements[-limit:]

        embed = discord.Embed(
            title=f"📢 Recent Announcements - {interaction.guild.name}",
            description=f"Showing {len(recent)} most recent announcements",
            color=discord.Color.blue(),
        )

        for ann_id in reversed(recent):
            announcement = self.announcements.get(ann_id)
            if not announcement:
                announcement = self._load_announcement(ann_id)

            if announcement:
                created = datetime.fromisoformat(announcement.created_at)
                author = interaction.guild.get_member(announcement.author_id)
                author_name = author.display_name if author else "Unknown"

                delivery_icons = {"public": "📢", "dm": "📨", "both": "📢📨"}

                value = (
                    f"{delivery_icons.get(announcement.delivery_mode, '📢')} **{announcement.delivery_mode.title()}**\n"
                    f"👤 By: {author_name}\n"
                    f"📅 {created.strftime('%Y-%m-%d %H:%M')}\n"
                    f"💬 {announcement.questions_asked} questions\n"
                    f"📊 {announcement.views} views"
                )

                if announcement.tags:
                    value += f"\n🏷️ {', '.join(f'`{t}`' for t in announcement.tags[:3])}"

                embed.add_field(name=f"{announcement.title}", value=value, inline=False)

        embed.set_footer(
            text="Use /ask_announcement <id> <question> to ask about any announcement"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="announcement_stats")
    @app_commands.describe(
        announcement_id="The announcement ID (or use 'latest' for most recent)"
    )
    async def announcement_stats(
        self, interaction: discord.Interaction, announcement_id: str
    ):
        """📊 View detailed statistics for an announcement"""

        # Handle 'latest'
        if announcement_id.lower() == "latest":
            guild_announcements = self.guild_announcements.get(interaction.guild_id, [])
            if not guild_announcements:
                await interaction.response.send_message(
                    "❌ No announcements found in this server.", ephemeral=True
                )
                return
            announcement_id = guild_announcements[-1]

        # Get announcement
        announcement = self.announcements.get(announcement_id)
        if not announcement:
            announcement = self._load_announcement(announcement_id)

        if not announcement:
            await interaction.response.send_message(
                "❌ Announcement not found.", ephemeral=True
            )
            return

        # Create stats embed
        embed = discord.Embed(
            title=f"📊 Statistics: {announcement.title}", color=discord.Color.green()
        )

        # Basic info
        created = datetime.fromisoformat(announcement.created_at)
        author = interaction.guild.get_member(announcement.author_id)

        embed.add_field(
            name="📝 Details",
            value=(
                f"**Created:** {created.strftime('%Y-%m-%d %H:%M')}\n"
                f"**Author:** {author.mention if author else 'Unknown'}\n"
                f"**Delivery:** {announcement.delivery_mode.title()}\n"
                f"**ID:** `{announcement_id}`"
            ),
            inline=False,
        )

        # Engagement stats
        embed.add_field(
            name="📈 Engagement",
            value=(
                f"**Views:** {announcement.views}\n"
                f"**Questions Asked:** {announcement.questions_asked}\n"
                f"**DMs Sent:** {announcement.dm_sent}\n"
                f"**DM Failures:** {announcement.dm_failed}"
            ),
            inline=True,
        )

        # Content analysis
        if announcement.key_points:
            embed.add_field(
                name="🎯 Key Points",
                value="\n".join(f"• {point}" for point in announcement.key_points[:3]),
                inline=False,
            )

        if announcement.summary:
            embed.add_field(name="📄 Summary", value=announcement.summary, inline=False)

        # Recent questions
        recent_questions = self._get_recent_questions(announcement_id, limit=3)
        if recent_questions:
            questions_text = "\n".join(
                (
                    f"• {q['question'][:100]}..."
                    if len(q["question"]) > 100
                    else f"• {q['question']}"
                )
                for q in recent_questions
            )
            embed.add_field(
                name="💬 Recent Questions", value=questions_text, inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="mod_announcement")
    @app_commands.describe(
        title="Announcement title",
        content="Announcement content (use \\n for line breaks)",
        send_to_all="Also send DM to all members (default: False)",
    )
    async def mod_announcement(
        self,
        interaction: discord.Interaction,
        title: str,
        content: str,
        send_to_all: bool = False,
    ):
        """🛡️ Quick announcement for mods/admins - posts to moderation channel"""

        # Permission check
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need 'Manage Server' permission to create mod announcements.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Get mod updates channel
            mod_channel = interaction.guild.get_channel(self.MOD_UPDATES_CHANNEL_ID)
            if not mod_channel:
                await interaction.followup.send(
                    f"❌ Moderation updates channel not found (ID: {self.MOD_UPDATES_CHANNEL_ID})",
                    ephemeral=True,
                )
                return

            # Process content
            content = content.replace("\\n", "\n")

            # Add mod badge to title
            if not title.startswith("🛡️"):
                title = f"🛡️ {title}"

            # Generate unique ID
            announcement_id = (
                f"{interaction.guild_id}_{int(datetime.now().timestamp())}"
            )

            # AI analysis
            await interaction.followup.send(
                "🤖 Analyzing mod announcement with AI...", ephemeral=True
            )

            analysis = await self.analyze_announcement_with_ai(title, content)

            # Determine delivery mode
            delivery_mode = "both" if send_to_all else "public"

            # Create announcement object
            announcement = AnnouncementData(
                announcement_id=announcement_id,
                title=title,
                content=content,
                author_id=interaction.user.id,
                guild_id=interaction.guild_id,
                created_at=datetime.now().isoformat(),
                delivery_mode=delivery_mode,
                channel_id=mod_channel.id,
                key_points=analysis.get("key_points", []),
                summary=analysis.get("summary", ""),
                faq=analysis.get("faq", {}),
                tags=analysis.get("tags", []),
            )

            # Save to database
            await self._save_announcement(announcement)

            # Cache announcement
            self.announcements[announcement_id] = announcement
            if interaction.guild_id not in self.guild_announcements:
                self.guild_announcements[interaction.guild_id] = []
            self.guild_announcements[interaction.guild_id].append(announcement_id)

            # Create announcement embed with mod styling
            embed = self._create_announcement_embed(announcement, interaction.user)
            embed.color = discord.Color.gold()  # Gold color for mod announcements

            # Send to mod channel
            sent_messages = []
            try:
                msg = await mod_channel.send(embed=embed)
                sent_messages.append(f"✅ Posted in {mod_channel.mention}")
                await msg.add_reaction("❓")
                await msg.add_reaction("📌")
            except Exception as e:
                self.logger.error(f"Error sending to mod channel: {e}")
                sent_messages.append(f"❌ Failed to post in {mod_channel.mention}")

            # Handle DMs if requested
            if send_to_all:
                members = [m for m in interaction.guild.members if not m.bot]
                announcement.dm_sent = 0
                announcement.dm_failed = 0

                if interaction.guild_id not in self.dm_queue:
                    self.dm_queue[interaction.guild_id] = []

                for member in members:
                    self.dm_queue[interaction.guild_id].append(
                        (member, embed, announcement_id)
                    )

                sent_messages.append(f"📬 Queued DMs for {len(members)} members")

            # Show analysis
            analysis_embed = discord.Embed(
                title="🛡️ Mod Announcement - AI Analysis Complete",
                description=f"**Summary:** {announcement.summary}",
                color=discord.Color.gold(),
            )

            if announcement.key_points:
                analysis_embed.add_field(
                    name="🎯 Key Points",
                    value="\n".join(
                        f"• {point}" for point in announcement.key_points[:5]
                    ),
                    inline=False,
                )

            if announcement.tags:
                analysis_embed.add_field(
                    name="🏷️ Tags",
                    value=", ".join(f"`{tag}`" for tag in announcement.tags[:5]),
                    inline=False,
                )

            analysis_embed.add_field(
                name="📤 Delivery Status", value="\n".join(sent_messages), inline=False
            )

            analysis_embed.add_field(
                name="💬 Q&A Feature",
                value=f"Use `/ask_announcement {announcement_id}` to answer questions!",
                inline=False,
            )

            await interaction.followup.send(embed=analysis_embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error creating mod announcement: {e}")
            await interaction.followup.send(
                f"❌ Error creating mod announcement: {str(e)}", ephemeral=True
            )

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _create_announcement_embed(
        self, announcement: AnnouncementData, author: discord.Member
    ) -> discord.Embed:
        """Create a beautiful embed for the announcement"""

        embed = discord.Embed(
            title=f"📢 {announcement.title}",
            description=announcement.content,
            color=discord.Color.blue(),
            timestamp=datetime.fromisoformat(announcement.created_at),
        )

        # Add AI summary if available
        if announcement.summary:
            embed.add_field(name="📝 Summary", value=announcement.summary, inline=False)

        # Add key points
        if announcement.key_points:
            points_text = "\n".join(
                f"• {point}" for point in announcement.key_points[:5]
            )
            embed.add_field(name="🎯 Key Points", value=points_text, inline=False)

        # Add FAQ preview - handle both dict and list formats
        if announcement.faq:
            if isinstance(announcement.faq, dict):
                faq_preview = list(announcement.faq.items())[:2]
                faq_text = "\n\n".join(
                    (
                        f"**Q: {q}**\nA: {a[:100]}..."
                        if len(a) > 100
                        else f"**Q: {q}**\nA: {a}"
                    )
                    for q, a in faq_preview
                )
            elif isinstance(announcement.faq, list):
                faq_preview = announcement.faq[:2]
                faq_text = "\n\n".join(
                    (
                        f"**Q: {item['q']}**\nA: {item['a'][:100]}..."
                        if len(item["a"]) > 100
                        else f"**Q: {item['q']}**\nA: {item['a']}"
                    )
                    for item in faq_preview
                    if "q" in item and "a" in item
                )
            else:
                faq_text = None

            if faq_text:
                embed.add_field(
                    name="❓ Common Questions", value=faq_text, inline=False
                )

        embed.set_author(
            name=f"Announcement by {author.display_name}",
            icon_url=author.display_avatar.url,
        )

        embed.set_footer(
            text=f"React with ❓ or use /ask_announcement to ask questions • ID: {announcement.announcement_id}"
        )

        return embed

    async def _save_announcement(self, announcement: AnnouncementData):
        """Save announcement to database"""
        try:
            await self.db.execute(
                """
                INSERT OR REPLACE INTO announcements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    announcement.announcement_id,
                    announcement.title,
                    announcement.content,
                    announcement.author_id,
                    announcement.guild_id,
                    announcement.created_at,
                    announcement.delivery_mode,
                    announcement.channel_id,
                    json.dumps(announcement.key_points),
                    announcement.summary,
                    json.dumps(announcement.faq),
                    json.dumps(announcement.tags),
                    announcement.views,
                    json.dumps(announcement.reactions),
                    announcement.questions_asked,
                    announcement.dm_sent,
                    announcement.dm_failed,
                ),
            )
        except Exception as e:
            self.logger.error(f"Error saving announcement: {e}")

    def _load_announcement(self, announcement_id: str) -> Optional[AnnouncementData]:
        """Load announcement from database"""
        try:
            result = self.db.fetchone(
                "SELECT * FROM announcements WHERE announcement_id = ?",
                (announcement_id,),
            )

            if result:
                return AnnouncementData(
                    announcement_id=result[0],
                    title=result[1],
                    content=result[2],
                    author_id=result[3],
                    guild_id=result[4],
                    created_at=result[5],
                    delivery_mode=result[6],
                    channel_id=result[7],
                    key_points=json.loads(result[8]) if result[8] else [],
                    summary=result[9] or "",
                    faq=json.loads(result[10]) if result[10] else {},
                    tags=json.loads(result[11]) if result[11] else [],
                    views=result[12],
                    reactions=json.loads(result[13]) if result[13] else {},
                    questions_asked=result[14],
                    dm_sent=result[15],
                    dm_failed=result[16],
                )
        except Exception as e:
            self.logger.error(f"Error loading announcement: {e}")

        return None

    async def _update_announcement_stats(self, announcement: AnnouncementData):
        """Update announcement statistics in database"""
        try:
            await self.db.execute(
                """
                UPDATE announcements
                SET views = ?, reactions = ?, questions_asked = ?, dm_sent = ?, dm_failed = ?
                WHERE announcement_id = ?
            """,
                (
                    announcement.views,
                    json.dumps(announcement.reactions),
                    announcement.questions_asked,
                    announcement.dm_sent,
                    announcement.dm_failed,
                    announcement.announcement_id,
                ),
            )
        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")

    async def _save_question(
        self, announcement_id: str, user_id: int, question: str, answer: str
    ):
        """Save Q&A to database"""
        try:
            await self.db.execute(
                """
                INSERT INTO announcement_questions (announcement_id, user_id, question, answer, asked_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    announcement_id,
                    user_id,
                    question,
                    answer,
                    datetime.now().isoformat(),
                ),
            )

            # Update cache
            if announcement_id not in self.announcement_questions:
                self.announcement_questions[announcement_id] = []

            self.announcement_questions[announcement_id].append(
                {
                    "question": question,
                    "answer": answer,
                    "user_id": user_id,
                    "asked_at": datetime.now().isoformat(),
                }
            )

            # Keep only last 20 questions in cache
            if len(self.announcement_questions[announcement_id]) > 20:
                self.announcement_questions[announcement_id] = (
                    self.announcement_questions[announcement_id][-20:]
                )

        except Exception as e:
            self.logger.error(f"Error saving question: {e}")

    def _get_recent_questions(self, announcement_id: str, limit: int = 5) -> List[Dict]:
        """Get recent questions for an announcement"""
        try:
            results = self.db.fetchall(
                """
                SELECT question, answer, user_id, asked_at
                FROM announcement_questions
                WHERE announcement_id = ?
                ORDER BY asked_at DESC
                LIMIT ?
            """,
                (announcement_id, limit),
            )

            return [
                {"question": r[0], "answer": r[1], "user_id": r[2], "asked_at": r[3]}
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error fetching questions: {e}")
            return []

    # ============================================================================
    # BACKGROUND TASKS
    # ============================================================================

    @tasks.loop(seconds=1.5)
    async def process_dm_queue_task(self):
        """Process DM queue with optimized rate limiting"""
        if not self.dm_queue:
            return

        try:
            guilds_to_process = list(self.dm_queue.keys())

            for guild_id in guilds_to_process:
                if guild_id not in self.dm_queue:
                    continue

                queue = self.dm_queue[guild_id]

                if not queue:
                    del self.dm_queue[guild_id]
                    continue

                # Process one DM per guild per iteration
                member, embed, announcement_id = queue.pop(0)

                try:
                    await member.send(embed=embed)

                    # Update stats atomically
                    if announcement_id in self.announcements:
                        announcement = self.announcements[announcement_id]
                        announcement.dm_sent += 1
                        await self._update_announcement_stats(announcement)

                    self.logger.debug(
                        f"✅ DM sent to {member.display_name} ({len(queue)} remaining in queue)"
                    )

                except discord.errors.Forbidden:
                    # User has DMs disabled
                    if announcement_id in self.announcements:
                        announcement = self.announcements[announcement_id]
                        announcement.dm_failed += 1
                        await self._update_announcement_stats(announcement)
                    self.logger.debug(f"Cannot DM {member.display_name} (DMs disabled)")

                except Exception as e:
                    if announcement_id in self.announcements:
                        announcement = self.announcements[announcement_id]
                        announcement.dm_failed += 1
                        await self._update_announcement_stats(announcement)
                    self.logger.error(f"❌ DM error for {member.display_name}: {e}")

                # Small delay between DMs (rate limiting)
                await asyncio.sleep(self.dm_rate_limit)

        except Exception as e:
            self.logger.error(f"Error in DM queue processing: {e}")

    @process_dm_queue_task.before_loop
    async def before_dm_queue(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def cleanup_old_data_task(self):
        """Clean up old announcement data"""
        try:
            # Remove announcements older than 90 days from cache
            cutoff = datetime.now() - timedelta(days=90)

            for ann_id in list(self.announcements.keys()):
                announcement = self.announcements[ann_id]
                created = datetime.fromisoformat(announcement.created_at)

                if created < cutoff:
                    del self.announcements[ann_id]

                    # Remove from guild list
                    for guild_list in self.guild_announcements.values():
                        if ann_id in guild_list:
                            guild_list.remove(ann_id)

            self.logger.info("✅ Cleaned up old announcement data from cache")

        except Exception as e:
            self.logger.error(f"Error in cleanup task: {e}")

    @cleanup_old_data_task.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    # ============================================================================
    # REACTION HANDLERS
    # ============================================================================

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reactions to announcements"""
        if user.bot:
            return

        # Check if it's a question reaction on an announcement
        if str(reaction.emoji) == "❓":
            # Find if this message is an announcement
            for announcement in self.announcements.values():
                if (
                    announcement.channel_id == reaction.message.channel.id
                    and announcement.delivery_mode in ["public", "both"]
                ):

                    # Send a helpful message
                    try:
                        await user.send(
                            f"❓ **Ask about: {announcement.title}**\n\n"
                            f"Use this command to ask your question:\n"
                            f"```\n/ask_announcement {announcement.announcement_id} Your question here\n```\n"
                            f"I'll use AI to answer based on the announcement content! 🤖"
                        )
                    except discord.errors.Forbidden:
                        pass  # User has DMs disabled

                    break

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.process_dm_queue_task.cancel()
        self.cleanup_old_data_task.cancel()


async def setup(bot):
    await bot.add_cog(AIAnnouncements(bot))
