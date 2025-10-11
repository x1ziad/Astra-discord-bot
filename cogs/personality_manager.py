"""
import time
from functools import lru_cache, wraps
import weakref
import gc
Astra Personality Management Commands
User interface for configuring Astra's personality parameters and modes
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
import asyncio
import random

from utils.astra_personality import get_personality_core, AstraMode
from core.unified_security_system import UnifiedSecuritySystem
from utils.permissions import has_permission, PermissionLevel, check_user_permission



def performance_monitor(func):
    """Monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start_time
            if duration > 1.0:  # Log slow operations
                print(f"⚠️ Slow operation {func.__name__}: {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start_time
            print(f"❌ Error in {func.__name__} after {duration:.3f}s: {e}")
            raise
    return wrapper

class ResetConfirmationView(discord.ui.View):
    """View for confirming personality reset"""

    def __init__(self):
        super().__init__(timeout=60)
        self.confirmed = None

    @discord.ui.button(label="✅ Yes, Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_reset(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.confirmed = False
        self.stop()
        await interaction.response.defer()


class PersonalityManager(commands.GroupCog, name="astra"):
    """Personality configuration and management system"""

    def __init__(self, bot):
        self.bot = bot
        self.security_system = UnifiedSecuritySystem(bot)

    @app_commands.command(
        name="personality",
        description="🧠 View Astra's current personality configuration",
    )
    async def personality_view(self, interaction: discord.Interaction):
        """View current personality configuration"""
        await interaction.response.defer()

        core = get_personality_core(interaction.guild.id if interaction.guild else None)

        embed = discord.Embed(
            title="🧠 Astra Personality Core",
            description="Current configuration and operational status",
            color=0x7C3AED,
        )

        # Current mode with emoji
        mode_emojis = {
            AstraMode.SECURITY: "🛡️",
            AstraMode.SOCIAL: "🎉",
            AstraMode.DEVELOPER: "🧩",
            AstraMode.MISSION_CONTROL: "📡",
            AstraMode.ADAPTIVE: "🧠",
        }

        embed.add_field(
            name="Current Mode",
            value=f"{mode_emojis.get(core.current_mode, '🔧')} **{core.current_mode.value.replace('_', ' ').title()}**",
            inline=True,
        )

        # Personality parameters with bars
        params = core.parameters.to_dict()
        param_display = ""

        for param, value in params.items():
            bar_filled = "█" * (value // 10)
            bar_empty = "░" * (10 - value // 10)
            param_display += (
                f"**{param.title()}:** `{bar_filled}{bar_empty}` {value}%\n"
            )

        embed.add_field(
            name="Personality Parameters", value=param_display, inline=False
        )

        # Quick actions
        embed.add_field(
            name="Available Commands",
            value=(
                "</astra set:1234567890> - Adjust personality traits\n"
                "</astra mode:1234567890> - Switch operational modes\n"
                "</astra reset:1234567890> - Reset to defaults\n"
                "</astra test:1234567890> - Simulate responses"
            ),
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="set",
        description="⚙️ Adjust Astra's personality traits and behavioral settings",
    )
    async def personality_set(
        self,
        interaction: discord.Interaction,
        trait: Literal[
            "humor",
            "honesty",
            "formality",
            "empathy",
            "strictness",
            "initiative",
            "transparency",
        ],
        value: app_commands.Range[int, 0, 100],
    ):
        """Set a specific personality parameter (0-100)"""
        await interaction.response.defer()

        # Security check
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only administrators can modify my personality settings.",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        # Set parameter
        core = get_personality_core(interaction.guild.id if interaction.guild else None)
        setattr(core.parameters, trait.lower(), value)
        core.save_personality()

        # Create visual feedback
        bar_filled = "█" * (value // 10)
        bar_empty = "░" * (10 - value // 10)

        embed = discord.Embed(
            title="✅ Personality Updated",
            description=f"**{trait.title()}** adjusted to {value}%\n`{bar_filled}{bar_empty}`",
            color=0x00FF7F,
        )

        # Add context-specific messages
        if trait == "humor" and value > 80:
            embed.add_field(
                name="🎭 Response Preview",
                value="I'm feeling extra witty today! Expect more jokes and playful banter! 😄",
                inline=False,
            )
        elif trait == "strictness" and value > 90:
            embed.add_field(
                name="🛡️ Security Enhanced",
                value="Zero tolerance protocols activated. I'll be much more firm with rule enforcement.",
                inline=False,
            )
        elif trait == "empathy" and value > 85:
            embed.add_field(
                name="💙 Emotional Intelligence",
                value="My emotional sensors are highly attuned. I'm here to support the crew.",
                inline=False,
            )
        elif trait == "formality" and value < 20:
            embed.add_field(
                name="😎 Casual Mode",
                value="Time to drop the professional act! I'll be much more relaxed and casual.",
                inline=False,
            )
        elif trait == "transparency" and value > 90:
            embed.add_field(
                name="🔍 Full Transparency",
                value="I'll explain my reasoning behind every action and decision I make.",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="mode", description="🎭 Switch between pre-configured personality modes"
    )
    async def personality_mode(
        self,
        interaction: discord.Interaction,
        mode: Literal["security", "social", "developer", "mission_control", "adaptive"],
    ):
        """Switch Astra's operational mode"""
        await interaction.response.defer()

        # Security check
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only administrators can modify my personality settings.",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        # Set new mode
        new_mode = AstraMode(mode.lower().replace(" ", "_"))
        core = get_personality_core(interaction.guild.id if interaction.guild else None)
        response_message = core.set_mode(new_mode)

        embed = discord.Embed(
            title="✅ Mode Changed", description=response_message, color=0x00FF7F
        )

        # Add mode-specific details
        mode_details = {
            "security": "• Strictness: 90% • Humor: 20% • Formality: 80%",
            "social": "• Humor: 80% • Empathy: 90% • Formality: 20%",
            "developer": "• Formality: 90% • Honesty: 100% • Transparency: 100%",
            "mission_control": "• Initiative: 95% • Transparency: 100% • Formality: 70%",
            "adaptive": "• All parameters balanced for context-aware responses",
        }

        embed.add_field(
            name="Parameter Changes", value=mode_details[mode], inline=False
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="reset",
        description="🔄 Reset Astra's personality traits to default values",
    )
    async def reset_personality(self, interaction: discord.Interaction):
        """Reset personality to default values"""
        await interaction.response.defer()

        # Security check
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only administrators can reset my personality settings.",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        # Confirmation embed
        embed = discord.Embed(
            title="⚠️ Confirm Personality Reset",
            description="This will reset all personality parameters to their default values:\n\n"
            "• **Humor**: 65% (Balanced wit)\n"
            "• **Honesty**: 90% (Very direct)\n"
            "• **Formality**: 40% (Casual-professional)\n"
            "• **Empathy**: 75% (Warm and caring)\n"
            "• **Strictness**: 60% (Moderate enforcement)\n"
            "• **Initiative**: 80% (Proactive suggestions)\n"
            "• **Transparency**: 95% (Explains actions)\n\n"
            "**Are you sure you want to proceed?**",
            color=0xF39C12,
        )

        # Create view with buttons
        view = ResetConfirmationView()
        await interaction.followup.send(embed=embed, view=view)

        # Wait for user response
        await view.wait()

        if view.confirmed:
            # Reset personality
            core = get_personality_core(
                interaction.guild.id if interaction.guild else None
            )
            response_message = core.set_mode(
                AstraMode.ADAPTIVE
            )  # This resets to defaults

            embed = discord.Embed(
                title="✅ Personality Reset Complete",
                description=response_message,
                color=0x00FF7F,
            )
            embed.add_field(
                name="All Parameters Reset",
                value="Astra's personality has been restored to balanced defaults.",
                inline=False,
            )
        else:
            embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="Personality settings remain unchanged.",
                color=0x95A5A6,
            )

        # Edit the original message
        try:
            await interaction.edit_original_response(embed=embed, view=None)
        except:
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="test",
        description="🧪 Simulate a sample response using current personality settings",
    )
    async def test_personality(self, interaction: discord.Interaction):
        """Simulate a sample response using current personality settings"""
        await interaction.response.defer()

        core = get_personality_core(interaction.guild.id if interaction.guild else None)
        params = core.parameters.to_dict()

        # Generate test scenarios based on personality
        test_scenarios = [
            "someone asks for help with a problem",
            "a user makes a joke in chat",
            "someone breaks a minor server rule",
            "a new member joins the server",
            "someone asks about your capabilities",
            "there's a heated argument in chat",
            "someone compliments the server",
            "a user seems frustrated or upset",
        ]

        scenario = random.choice(test_scenarios)

        # Generate personality-based response
        response_samples = {
            "high_humor": [
                "Well, that's quite the situation! Let me work my magic... ✨",
                "Oh, this should be fun! *cracks digital knuckles* 😄",
                "Time to put on my problem-solving cape! 🦸‍♀️",
            ],
            "low_humor": [
                "I'll address this matter immediately.",
                "Understood. Processing your request.",
                "Acknowledged. Initiating appropriate response.",
            ],
            "high_empathy": [
                "I understand this might be frustrating for you. Let me help! 💙",
                "I can sense you're dealing with something difficult. I'm here to support you.",
                "That sounds challenging. Let's work through this together! 🤗",
            ],
            "low_empathy": [
                "Here's the information you requested.",
                "This is the standard procedure for this situation.",
                "Completing task as specified.",
            ],
            "high_strictness": [
                "I need to address this rule violation immediately. No exceptions.",
                "This behavior is unacceptable and will be dealt with accordingly.",
                "Security protocols require immediate action. Stand by.",
            ],
            "low_strictness": [
                "Hey, maybe we could try a different approach here?",
                "I get it, but let's keep things friendly, yeah? 😊",
                "No worries! We all make mistakes sometimes.",
            ],
        }

        # Select appropriate response based on parameters
        if params["humor"] > 70:
            sample_response = random.choice(response_samples["high_humor"])
        elif params["humor"] < 30:
            sample_response = random.choice(response_samples["low_humor"])
        elif params["empathy"] > 80:
            sample_response = random.choice(response_samples["high_empathy"])
        elif params["empathy"] < 30:
            sample_response = random.choice(response_samples["low_empathy"])
        elif params["strictness"] > 80:
            sample_response = random.choice(response_samples["high_strictness"])
        elif params["strictness"] < 30:
            sample_response = random.choice(response_samples["low_strictness"])
        else:
            sample_response = (
                "Let me think about the best way to handle this situation... 🤔"
            )

        embed = discord.Embed(
            title="🧪 Personality Test Simulation",
            description=f"**Scenario:** When {scenario}",
            color=0x9B59B6,
        )

        embed.add_field(
            name="🎭 Astra's Response", value=f'*"{sample_response}"*', inline=False
        )

        # Show dominant traits affecting this response
        dominant_traits = sorted(params.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_influence = " • ".join(
            [f"{trait.title()}: {value}%" for trait, value in dominant_traits]
        )

        embed.add_field(
            name="🔍 Dominant Personality Traits", value=trait_influence, inline=False
        )

        # Add mode context
        embed.add_field(
            name="🎯 Current Mode",
            value=f"{core.current_mode.value.replace('_', ' ').title()} Mode",
            inline=True,
        )

        embed.set_footer(
            text="💡 Tip: Use /astra set to adjust traits and see how responses change!"
        )

        await interaction.followup.send(embed=embed)

    @commands.command(name="astrastatus", aliases=["status"])
    async def astra_status(self, ctx):
        """Get Astra's current operational status"""

        core = get_personality_core(ctx.guild.id if ctx.guild else None)
        status_message = core.get_system_status_message()

        embed = discord.Embed(
            title="🌟 Astra Status Report",
            description=status_message,
            color=0x7C3AED,
            timestamp=discord.utils.utcnow(),
        )

        # Add system info
        embed.add_field(
            name="Operational Mode",
            value=core.current_mode.value.replace("_", " ").title(),
            inline=True,
        )

        embed.add_field(
            name="Guild ID",
            value=str(ctx.guild.id) if ctx.guild else "DM Channel",
            inline=True,
        )

        # Add personality quick-view
        params = core.parameters.to_dict()
        top_traits = sorted(params.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_text = " • ".join(
            [f"{trait.title()}: {value}%" for trait, value in top_traits]
        )

        embed.add_field(name="Dominant Traits", value=trait_text, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    cog = PersonalityManager(bot)
    await bot.add_cog(cog)
