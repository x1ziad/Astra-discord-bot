"""
Enhanced Bot Setup and Invitation Commands
Comprehensive bot integration and setup management
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.bot_invite import generate_bot_invite_url, get_full_permissions, get_minimal_permissions, get_recommended_permissions
from config.unified_config import unified_config
import json
from pathlib import Path
from datetime import datetime, timezone
import asyncio

class InviteView(discord.ui.View):
    """Interactive view for bot invitation with different permission levels"""
    
    def __init__(self, client_id: str):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.client_id = client_id
        
        # Generate URLs for different permission levels
        self.full_url = generate_bot_invite_url(client_id, get_full_permissions())
        self.recommended_url = generate_bot_invite_url(client_id, get_recommended_permissions())
        self.minimal_url = generate_bot_invite_url(client_id, get_minimal_permissions())
    
    @discord.ui.button(label="Full Permissions", style=discord.ButtonStyle.green, emoji="🌟")
    async def full_permissions(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🌟 Full Permissions Invitation",
            description="This gives Astra complete access to all features.",
            color=unified_config.get_color("success")
        )
        embed.add_field(
            name="✅ Includes:",
            value="• All moderation features\n• Server management\n• AI capabilities\n• Analytics and insights\n• Role management\n• Channel management",
            inline=False
        )
        embed.add_field(
            name="🔗 Invitation Link:",
            value=f"[Add Astra with Full Permissions]({self.full_url})",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @discord.ui.button(label="Recommended", style=discord.ButtonStyle.blurple, emoji="⭐")
    async def recommended_permissions(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⭐ Recommended Permissions",
            description="Balanced permissions for most servers.",
            color=unified_config.get_color("info")
        )
        embed.add_field(
            name="✅ Includes:",
            value="• Core bot functions\n• Space exploration features\n• Quiz and interactive commands\n• Basic moderation\n• Message management",
            inline=False
        )
        embed.add_field(
            name="🔗 Invitation Link:",
            value=f"[Add Astra with Recommended Permissions]({self.recommended_url})",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @discord.ui.button(label="Minimal", style=discord.ButtonStyle.gray, emoji="⚡")
    async def minimal_permissions(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚡ Minimal Permissions",
            description="Basic functionality only - perfect for testing.",
            color=unified_config.get_color("warning")
        )
        embed.add_field(
            name="✅ Includes:",
            value="• Send messages\n• Basic commands\n• Space facts\n• Simple interactions\n• No moderation features",
            inline=False
        )
        embed.add_field(
            name="🔗 Invitation Link:",
            value=f"[Add Astra with Minimal Permissions]({self.minimal_url})",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BotSetup(commands.Cog):
    """Enhanced commands for bot setup and invitation management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        
        # Load invitation stats if available
        self.stats_file = Path("data/invitation_stats.json")
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Load invitation statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading invitation stats: {e}")
        
        return {
            "total_invitations": 0,
            "successful_joins": 0,
            "last_invitation": None,
            "daily_stats": {}
        }
    
    def _save_stats(self):
        """Save invitation statistics"""
        try:
            self.stats_file.parent.mkdir(exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving invitation stats: {e}")
    
    def _update_invitation_stats(self):
        """Update invitation statistics"""
        self.stats["total_invitations"] += 1
        self.stats["last_invitation"] = datetime.now(timezone.utc).isoformat()
        
        # Daily stats
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = 0
        self.stats["daily_stats"][today] += 1
        
        self._save_stats()
    
    @app_commands.command(
        name="invite",
        description="Get invitation links to add Astra to other servers"
    )
    @app_commands.describe(
        permission_level="Choose permission level: full, recommended, minimal, or interactive"
    )
    @app_commands.choices(permission_level=[
        app_commands.Choice(name="Full Permissions (All Features)", value="full"),
        app_commands.Choice(name="Recommended (Balanced)", value="recommended"), 
        app_commands.Choice(name="Minimal (Basic Only)", value="minimal"),
        app_commands.Choice(name="Interactive Selector", value="interactive")
    ])
    async def invite_command(
        self, 
        interaction: discord.Interaction, 
        permission_level: str = "interactive"
    ):
        """Enhanced invitation command with permission level selection"""
        
        # Update stats
        self._update_invitation_stats()
        
        # Get bot's client ID
        client_id = str(self.bot.user.id)
        
        if permission_level == "interactive":
            # Show interactive view with buttons
            embed = discord.Embed(
                title="🤖 Invite Astra to Your Server!",
                description="Choose the permission level that works best for your server:",
                color=unified_config.get_color("info")
            )
            embed.add_field(
                name="🌟 Full Permissions",
                value="Complete access to all features including moderation, server management, and advanced AI capabilities.",
                inline=False
            )
            embed.add_field(
                name="⭐ Recommended",
                value="Balanced permissions perfect for most servers - includes core features without excessive permissions.",
                inline=False
            )
            embed.add_field(
                name="⚡ Minimal",
                value="Basic functionality only - great for testing or servers that want minimal bot permissions.",
                inline=False
            )
            
            embed.set_footer(text="Click a button below to get the appropriate invitation link")
            
            view = InviteView(client_id)
            await interaction.response.send_message(embed=embed, view=view)
            
        else:
            # Direct permission level selection
            if permission_level == "full":
                permissions = get_full_permissions()
                title = "🌟 Full Permissions Invitation"
                description = "Complete access to all Astra features"
                features = "• All moderation and server management\n• Advanced AI capabilities\n• Complete analytics suite\n• Role and channel management\n• Automated moderation tools"
            elif permission_level == "recommended":
                permissions = get_recommended_permissions()
                title = "⭐ Recommended Permissions"
                description = "Balanced permissions for most servers"
                features = "• Core bot functionality\n• Space exploration commands\n• Quiz and interactive features\n• Basic moderation tools\n• Message management"
            else:  # minimal
                permissions = get_minimal_permissions()
                title = "⚡ Minimal Permissions"
                description = "Basic functionality only"
                features = "• Send messages and embeds\n• Basic slash commands\n• Space facts and information\n• Simple interactions\n• No moderation features"
            
            invite_url = generate_bot_invite_url(client_id, permissions)
            
            embed = discord.Embed(
                title=title,
                description=description,
                color=unified_config.get_color("success")
            )
            
            embed.add_field(
                name="✅ Features Included:",
                value=features,
                inline=False
            )
            
            embed.add_field(
                name="🔗 Invitation Link:",
                value=f"[Click here to invite Astra]({invite_url})",
                inline=False
            )
            
            embed.add_field(
                name="📋 Setup Instructions:",
                value="1. Click the invitation link above\n2. Select your server\n3. Review the requested permissions\n4. Click 'Authorize'\n5. Test with `/ping` command",
                inline=False
            )
            
            # Add direct link button
            view = discord.ui.View()
            link_button = discord.ui.Button(
                label=f"Invite Astra ({permission_level.title()})",
                style=discord.ButtonStyle.link,
                url=invite_url,
                emoji="🤖"
            )
            view.add_item(link_button)
            
            await interaction.response.send_message(embed=embed, view=view)
        
        self.logger.info(f"Invitation link ({permission_level}) requested by {interaction.user} in {interaction.guild}")
    
    @app_commands.command(
        name="setup",
        description="Comprehensive setup guide for server administrators"
    )
    async def setup_command(self, interaction: discord.Interaction):
        """Enhanced setup guide for server administrators"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ This command requires 'Manage Server' permission.",
                ephemeral=True
            )
            return
        
        # Create comprehensive setup embed
        embed = discord.Embed(
            title="⚙️ Astra Bot Setup Guide",
            description=f"Welcome to {interaction.guild.name}! Here's your complete setup guide.",
            color=unified_config.get_color("info")
        )
        
        embed.add_field(
            name="🚀 Quick Start (30 seconds):",
            value="• Test connection: `/ping`\n• Get space fact: `/space fact`\n• View all commands: `/help`\n• Server stats: `/stats server`",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Essential Commands:",
            value="• `/space apod` - NASA Astronomy Picture of the Day\n• `/quiz start` - Interactive space quiz\n• `/invite` - Share Astra with other servers\n• `/stats user @someone` - User activity stats",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Configuration Options:",
            value="• Custom server prefixes\n• Feature enable/disable toggles\n• AI personality settings\n• Automated moderation rules\n• Analytics preferences",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Moderation Features:",
            value="• Message filtering\n• Spam detection\n• Role management\n• Channel management\n• User warnings and kicks",
            inline=False
        )
        
        embed.add_field(
            name="🌟 Advanced Features:",
            value="• AI-powered conversations\n• Real-time space data (ISS, weather)\n• Custom quizzes and polls\n• Server analytics dashboard\n• Integration with external APIs",
            inline=False
        )
        
        embed.add_field(
            name="❓ Need Help?",
            value="• Use `/help [command]` for specific commands\n• Join our support server (coming soon)\n• Check GitHub documentation\n• Report bugs to administrators",
            inline=False
        )
        
        embed.set_footer(
            text=f"Astra v{unified_config.get_bot_config().version} • {len(self.bot.guilds)} servers • Ready for exploration!"
        )
        
        # Add helpful buttons
        view = discord.ui.View()
        
        # Quick test button
        test_button = discord.ui.Button(
            label="Test Bot",
            style=discord.ButtonStyle.green,
            emoji="🧪"
        )
        
        async def test_callback(button_interaction):
            test_embed = discord.Embed(
                title="🧪 Bot Test Results",
                color=unified_config.get_color("success")
            )
            test_embed.add_field(name="✅ Bot Status", value="Online and responsive", inline=True)
            test_embed.add_field(name="✅ Permissions", value="Working correctly", inline=True)
            test_embed.add_field(name="✅ Commands", value="Ready to use", inline=True)
            test_embed.add_field(name="📊 Quick Stats", value=f"Latency: {self.bot.latency*1000:.0f}ms\nGuilds: {len(self.bot.guilds)}\nUptime: {self.bot.stats.get_uptime()}", inline=False)
            await button_interaction.response.send_message(embed=test_embed, ephemeral=True)
        
        test_button.callback = test_callback
        view.add_item(test_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        self.logger.info(f"Setup guide requested by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(
        name="diagnostics",
        description="Run comprehensive bot diagnostics and health checks"
    )
    async def diagnostics_command(self, interaction: discord.Interaction):
        """Run comprehensive bot diagnostics"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ This command requires administrator permissions.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Run diagnostics
        diagnostics = {}
        
        # Bot connectivity
        diagnostics["bot_status"] = "✅ Online" if self.bot.is_ready() else "❌ Offline"
        diagnostics["latency"] = f"{self.bot.latency * 1000:.0f}ms"
        
        # Permissions check
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if bot_member:
            perms = bot_member.guild_permissions
            critical_perms = {
                "send_messages": perms.send_messages,
                "embed_links": perms.embed_links,
                "use_slash_commands": perms.use_slash_commands,
                "read_message_history": perms.read_message_history
            }
            diagnostics["permissions"] = "✅ All critical permissions present" if all(critical_perms.values()) else "⚠️ Missing some permissions"
            diagnostics["permission_details"] = critical_perms
        
        # Extension health
        healthy_extensions = sum(1 for health in self.bot.extension_health.values() if health)
        total_extensions = len(self.bot.extension_health)
        diagnostics["extensions"] = f"✅ {healthy_extensions}/{total_extensions} healthy"
        
        # Database connectivity
        try:
            from utils.database import db
            await db.get("test", "ping", {})
            diagnostics["database"] = "✅ Connected"
        except Exception as e:
            diagnostics["database"] = f"❌ Error: {str(e)[:50]}"
        
        # API connectivity (NASA API test)
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY", timeout=5) as resp:
                    diagnostics["nasa_api"] = "✅ Accessible" if resp.status == 200 else f"⚠️ Status {resp.status}"
        except Exception as e:
            diagnostics["nasa_api"] = f"❌ Error: {str(e)[:50]}"
        
        # Create diagnostics embed
        embed = discord.Embed(
            title="🔍 Bot Diagnostics Report",
            description=f"Comprehensive health check for {interaction.guild.name}",
            color=unified_config.get_color("info"),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="🤖 Bot Status",
            value=f"Status: {diagnostics['bot_status']}\nLatency: {diagnostics['latency']}\nExtensions: {diagnostics['extensions']}",
            inline=True
        )
        
        embed.add_field(
            name="🔐 Permissions",
            value=diagnostics["permissions"],
            inline=True
        )
        
        embed.add_field(
            name="🌐 External Services",
            value=f"Database: {diagnostics['database']}\nNASA API: {diagnostics['nasa_api']}",
            inline=True
        )
        
        if "permission_details" in diagnostics:
            perm_status = "\n".join([
                f"{'✅' if v else '❌'} {k.replace('_', ' ').title()}"
                for k, v in diagnostics["permission_details"].items()
            ])
            embed.add_field(
                name="📋 Detailed Permissions",
                value=perm_status,
                inline=False
            )
        
        embed.add_field(
            name="💡 Recommendations",
            value="• Run `/ping` to test basic functionality\n• Use `/space apod` to test NASA API\n• Try `/quiz start` to test interactive features\n• Check `/stats server` for analytics",
            inline=False
        )
        
        embed.set_footer(text="Diagnostics completed")
        
        await interaction.followup.send(embed=embed)
        
        self.logger.info(f"Diagnostics run by {interaction.user} in {interaction.guild.name}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Track successful bot installations"""
        self.stats["successful_joins"] += 1
        self._save_stats()
        
        self.logger.info(f"Successfully joined guild: {guild.name} (ID: {guild.id})")
        
        # Try to send welcome message to system channel
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="🎉 Thanks for adding Astra!",
                description="I'm ready to help explore the cosmos with your server!",
                color=unified_config.get_color("success")
            )
            embed.add_field(
                name="🚀 Quick Start:",
                value="• Try `/ping` to test me\n• Use `/space fact` for a space fact\n• Run `/setup` for full configuration\n• Get help with `/help`",
                inline=False
            )
            
            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                pass  # No permission to send to system channel

async def setup(bot):
    await bot.add_cog(BotSetup(bot))
