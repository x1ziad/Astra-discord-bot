import discord
from discord.ext import commands
from datetime import datetime, timedelta
import psutil
import asyncio



class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        """Check bot latency and response time"""
        start_time = datetime.utcnow()

        # Create initial embed
        embed = discord.Embed(
            title="🏓 Pong!", description="Calculating latency...", color=0xFFFF00
        )
        message = await ctx.send(embed=embed)

        # Calculate response time
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Update embed with results
        embed = discord.Embed(
            title="🏓 Pong!",
            color=(
                0x00FF00
                if self.bot.latency * 1000 < 100
                else 0xFFFF00 if self.bot.latency * 1000 < 200 else 0xFF0000
            ),
        )

        embed.add_field(
            name="📡 WebSocket Latency",
            value=f"{self.bot.latency * 1000:.2f}ms",
            inline=True,
        )

        embed.add_field(
            name="⚡ Response Time", value=f"{response_time:.2f}ms", inline=True
        )

        # Add status indicator
        if self.bot.latency * 1000 < 100:
            status = "🟢 Excellent"
        elif self.bot.latency * 1000 < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"

        embed.add_field(name="📊 Status", value=status, inline=True)

        embed.set_footer(text=f"Shard ID: {ctx.guild.shard_id if ctx.guild else 'N/A'}")

        await message.edit(embed=embed)

    @commands.command(name="uptime")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uptime(self, ctx):
        """Show bot uptime and system information"""
        current_time = datetime.utcnow()
        uptime_duration = current_time - self.bot.start_time

        # Format uptime
        days = uptime_duration.days
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            title="⏰ Astra Bot Uptime", color=0x5865F2, timestamp=current_time
        )

        embed.add_field(
            name="🚀 Online Since",
            value=f"<t:{int(self.bot.start_time.timestamp())}:F>",
            inline=False,
        )

        embed.add_field(name="⏱️ Total Uptime", value=uptime_str, inline=True)

        # System information
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            embed.add_field(
                name="💻 System Stats",
                value=f"**CPU:** {cpu_percent}%\n**RAM:** {memory.percent}%",
                inline=True,
            )
        except:
            embed.add_field(
                name="💻 System Stats", value="Data unavailable", inline=True
            )

        embed.add_field(
            name="📊 Bot Stats",
            value=f"**Servers:** {len(self.bot.guilds)}\n**Users:** {len(set(self.bot.get_all_members()))}",
            inline=True,
        )

        embed.set_footer(text="Astra has been watching the cosmos")

        await ctx.send(embed=embed)

    @commands.command(name="stats")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def server_stats(self, ctx):
        """Display comprehensive server statistics"""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return

        # Calculate member statistics
        total_members = guild.member_count
        online_members = sum(
            1 for member in guild.members if member.status != discord.Status.offline
        )
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots

        # Channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        # Role statistics
        total_roles = len(guild.roles) - 1  # Exclude @everyone

        # Server boost information
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count

        embed = discord.Embed(
            title=f"📊 {guild.name} Statistics",
            color=0x5865F2,
            timestamp=datetime.utcnow(),
        )

        # Set server icon as thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Member statistics
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {total_members:,}\n**Humans:** {humans:,}\n**Bots:** {bots:,}\n**Online:** {online_members:,}",
            inline=True,
        )

        # Channel statistics
        embed.add_field(
            name="📝 Channels",
            value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}",
            inline=True,
        )

        # Server information
        embed.add_field(
            name="🏛️ Server Info",
            value=f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n**Roles:** {total_roles}",
            inline=True,
        )

        # Boost information
        if boost_count > 0:
            embed.add_field(
                name="✨ Nitro Boosts",
                value=f"**Level:** {boost_level}\n**Boosts:** {boost_count}",
                inline=True,
            )

        # Features
        features = []
        if "COMMUNITY" in guild.features:
            features.append("🌐 Community")
        if "PARTNERED" in guild.features:
            features.append("🤝 Partnered")
        if "VERIFIED" in guild.features:
            features.append("✅ Verified")
        if "VANITY_URL" in guild.features:
            features.append("🔗 Vanity URL")

        if features:
            embed.add_field(name="🎯 Features", value="\n".join(features), inline=True)

        # Verification level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest",
        }

        embed.add_field(
            name="🔒 Security",
            value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}",
            inline=True,
        )

        embed.set_footer(text=f"Server ID: {guild.id}")

        await ctx.send(embed=embed)

    @commands.command(name="membercount")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def member_count(self, ctx):
        """Show a detailed member count breakdown"""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return

        # Count members by status
        online = sum(
            1 for member in guild.members if member.status == discord.Status.online
        )
        idle = sum(
            1 for member in guild.members if member.status == discord.Status.idle
        )
        dnd = sum(1 for member in guild.members if member.status == discord.Status.dnd)
        offline = sum(
            1 for member in guild.members if member.status == discord.Status.offline
        )

        # Count bots vs humans
        bots = sum(1 for member in guild.members if member.bot)
        humans = guild.member_count - bots

        embed = discord.Embed(
            title="👥 Member Count Breakdown",
            color=0x00FF00,
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📊 Total Members",
            value=f"**{guild.member_count:,}** members",
            inline=False,
        )

        embed.add_field(
            name="🟢 Status Breakdown",
            value=f"🟢 Online: **{online:,}**\n🟡 Idle: **{idle:,}**\n🔴 DND: **{dnd:,}**\n⚫ Offline: **{offline:,}**",
            inline=True,
        )

        embed.add_field(
            name="🤖 Type Breakdown",
            value=f"👤 Humans: **{humans:,}**\n🤖 Bots: **{bots:,}**",
            inline=True,
        )

        # Calculate percentages
        online_percent = (
            (online / guild.member_count) * 100 if guild.member_count > 0 else 0
        )
        embed.add_field(
            name="📈 Activity",
            value=f"**{online_percent:.1f}%** currently online",
            inline=False,
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await ctx.send(embed=embed)

    @commands.command(name="roleinfo")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def role_info(self, ctx, *, role_name: str = None):
        """Get information about server roles or a specific role"""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return

        if role_name:
            # Find specific role
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description=f"No role named '{role_name}' found in this server.",
                    color=0xFF0000,
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"🏷️ Role: {role.name}",
                color=role.color if role.color != discord.Color.default() else 0x5865F2,
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="📊 Info",
                value=f"**Members:** {len(role.members)}\n**Position:** {role.position}\n**Mentionable:** {'Yes' if role.mentionable else 'No'}\n**Hoisted:** {'Yes' if role.hoist else 'No'}",
                inline=True,
            )

            embed.add_field(
                name="🎨 Appearance",
                value=f"**Color:** {str(role.color) if role.color != discord.Color.default() else 'Default'}\n**Created:** <t:{int(role.created_at.timestamp())}:R>",
                inline=True,
            )

            # Show some permissions if they exist
            if role.permissions.administrator:
                perms = "Administrator (All Permissions)"
            else:
                key_perms = []
                if role.permissions.manage_guild:
                    key_perms.append("Manage Server")
                if role.permissions.manage_channels:
                    key_perms.append("Manage Channels")
                if role.permissions.manage_roles:
                    key_perms.append("Manage Roles")
                if role.permissions.kick_members:
                    key_perms.append("Kick Members")
                if role.permissions.ban_members:
                    key_perms.append("Ban Members")

                perms = (
                    ", ".join(key_perms[:3]) if key_perms else "No special permissions"
                )
                if len(key_perms) > 3:
                    perms += f" (+{len(key_perms) - 3} more)"

            embed.add_field(name="🔑 Key Permissions", value=perms, inline=False)

            embed.set_footer(text=f"Role ID: {role.id}")

        else:
            # Show all roles overview
            roles = sorted(
                guild.roles[1:], key=lambda r: r.position, reverse=True
            )  # Exclude @everyone

            embed = discord.Embed(
                title=f"🏷️ {guild.name} Roles",
                description=f"Total roles: **{len(roles)}**",
                color=0x5865F2,
                timestamp=datetime.utcnow(),
            )

            # Show top roles
            top_roles = roles[:10]
            role_list = []
            for role in top_roles:
                member_count = len(role.members)
                role_list.append(f"**{role.name}** - {member_count} members")

            embed.add_field(
                name="🔝 Top Roles",
                value="\n".join(role_list) if role_list else "No roles found",
                inline=False,
            )

            if len(roles) > 10:
                embed.add_field(
                    name="ℹ️ Note",
                    value=f"Showing top 10 of {len(roles)} roles. Use `!roleinfo <role name>` for detailed info.",
                    inline=False,
                )

        await ctx.send(embed=embed)

    @commands.command(name="channelstats")
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def channel_stats(self, ctx):
        """Show channel statistics for the server"""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return

        # Count different channel types
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        stage_channels = len(guild.stage_channels)
        forum_channels = len(
            [
                ch
                for ch in guild.channels
                if hasattr(ch, "type") and str(ch.type) == "forum"
            ]
        )
        categories = len(guild.categories)

        embed = discord.Embed(
            title="📝 Channel Statistics", color=0x5865F2, timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="📊 Channel Count",
            value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Stage:** {stage_channels}\n**Categories:** {categories}",
            inline=True,
        )

        # Find most active text channel (by message count if available)
        embed.add_field(
            name="🏆 Most Active",
            value="Use `!activity` to see message statistics",
            inline=True,
        )

        # Voice channel info
        voice_members = sum(len(vc.members) for vc in guild.voice_channels)
        embed.add_field(
            name="🔊 Voice Activity",
            value=f"**Members in VC:** {voice_members}\n**Active Channels:** {sum(1 for vc in guild.voice_channels if len(vc.members) > 0)}",
            inline=True,
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
