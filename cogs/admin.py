"""
Administrative commands for Astra Bot
Provides bot management, server configuration, and moderation tools
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import traceback
from datetime import datetime, timedelta
import json
import os
from typing import Optional, List, Literal

from config.config_manager import config_manager


class Admin(commands.GroupCog, name="admin"):
    """Administrative commands for bot management"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

    @app_commands.command(
        name="reload", description="Reload a specific cog or all cogs"
    )
    @app_commands.describe(cog="The cog to reload, or 'all' to reload all cogs")
    @app_commands.default_permissions(administrator=True)
    async def reload_command(self, interaction: discord.Interaction, cog: str):
        """Reload a specific cog or all cogs (Admin only)"""
        # Check if user is bot owner
        app_info = await self.bot.application_info()
        is_owner = interaction.user.id == app_info.owner.id
        is_admin = interaction.user.guild_permissions.administrator

        if not is_owner and not is_admin:
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner or server administrators.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if cog.lower() == "all":
            # Reload all cogs
            success_cogs = []
            failed_cogs = []

            for ext in [
                f.replace(".py", "")
                for f in os.listdir("cogs")
                if f.endswith(".py") and not f.startswith("__")
            ]:
                ext_name = f"cogs.{ext}"
                try:
                    await self.bot.reload_extension(ext_name)
                    success_cogs.append(ext)
                except Exception as e:
                    failed_cogs.append(f"{ext}: {str(e)}")
                    self.logger.error(
                        f"Failed to reload {ext}: {traceback.format_exc()}"
                    )

            # Create results embed
            embed = discord.Embed(
                title="🔄 Reload Results",
                description=f"Successfully reloaded **{len(success_cogs)}** cog(s)",
                color=(
                    self.config.get_color("success")
                    if not failed_cogs
                    else self.config.get_color("warning")
                ),
                timestamp=datetime.utcnow(),
            )

            if success_cogs:
                embed.add_field(
                    name="✅ Success",
                    value="```\n" + "\n".join(success_cogs) + "\n```",
                    inline=False,
                )

            if failed_cogs:
                embed.add_field(
                    name="❌ Failed",
                    value="```\n" + "\n".join(failed_cogs)[:1000] + "\n```",
                    inline=False,
                )

            await interaction.followup.send(embed=embed)

        else:
            # Reload specific cog
            cog_name = cog if cog.startswith("cogs.") else f"cogs.{cog}"

            try:
                await self.bot.reload_extension(cog_name)
                embed = discord.Embed(
                    title="✅ Cog Reloaded",
                    description=f"Successfully reloaded `{cog_name}`",
                    color=self.config.get_color("success"),
                    timestamp=datetime.utcnow(),
                )
                await interaction.followup.send(embed=embed)

            except Exception as e:
                embed = discord.Embed(
                    title="❌ Reload Failed",
                    description=f"Error reloading `{cog_name}`:\n```\n{str(e)}\n```",
                    color=self.config.get_color("error"),
                    timestamp=datetime.utcnow(),
                )
                await interaction.followup.send(embed=embed)
                self.logger.error(
                    f"Failed to reload {cog_name}: {traceback.format_exc()}"
                )

    @app_commands.command(
        name="sync", description="Sync application commands to Discord"
    )
    @app_commands.describe(
        scope="Where to sync commands to (guild or global)",
        clear="Clear all commands first",
    )
    @app_commands.default_permissions(administrator=True)
    async def sync_command(
        self,
        interaction: discord.Interaction,
        scope: Literal["guild", "global"] = "guild",
        clear: bool = False,
    ):
        """Sync application commands to Discord (Admin only)"""
        # Check if user is bot owner
        app_info = await self.bot.application_info()
        is_owner = interaction.user.id == app_info.owner.id

        if not is_owner:
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if scope == "guild":
                if clear:
                    # Clear commands from guild first
                    self.bot.tree.clear_commands(guild=interaction.guild)
                    await self.bot.tree.sync(guild=interaction.guild)
                    await asyncio.sleep(2)  # Wait for commands to clear

                # Sync to current guild
                synced = await self.bot.tree.sync(guild=interaction.guild)
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Successfully synced **{len(synced)}** commands to this server.",
                    color=self.config.get_color("success"),
                    timestamp=datetime.utcnow(),
                )

            else:  # Global sync
                if clear:
                    # Clear global commands
                    self.bot.tree.clear_commands(guild=None)
                    await self.bot.tree.sync()
                    await asyncio.sleep(5)  # Wait longer for global commands

                # Sync globally
                synced = await self.bot.tree.sync()
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Successfully synced **{len(synced)}** commands globally.\n\n⚠️ **Note:** Global commands may take up to 1 hour to update.",
                    color=self.config.get_color("success"),
                    timestamp=datetime.utcnow(),
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"Error syncing commands:\n```\n{str(e)}\n```",
                color=self.config.get_color("error"),
                timestamp=datetime.utcnow(),
            )
            await interaction.followup.send(embed=embed)
            self.logger.error(f"Failed to sync commands: {traceback.format_exc()}")

    @app_commands.command(
        name="setup", description="Configure bot settings for this server"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):
        """Configure bot settings for this server (Admin only)"""
        # Import here to avoid circular imports
        from ui.ui_components import SetupModal

        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ This command can only be used by server administrators.",
                ephemeral=True,
            )
            return

        # Create and send the setup modal
        modal = SetupModal()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="config", description="View or change bot configuration")
    @app_commands.describe(
        setting="Configuration setting to view/change",
        value="New value for the setting",
    )
    @app_commands.default_permissions(administrator=True)
    async def config_command(
        self,
        interaction: discord.Interaction,
        setting: str,
        value: Optional[str] = None,
    ):
        """View or change bot configuration (Admin only)"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ This command can only be used by server administrators.",
                ephemeral=True,
            )
            return

        # Get current guild config
        guild_id = interaction.guild.id
        guild_config = self.config.load_guild_config(guild_id)

        # If just viewing a setting
        if value is None:
            # Find the setting in guild config
            try:
                keys = setting.split(".")
                current_value = guild_config

                for key in keys:
                    current_value = current_value[key]

                # Create embed with the setting info
                embed = discord.Embed(
                    title=f"⚙️ Configuration: {setting}",
                    description=f"Current value for `{setting}`:",
                    color=self.config.get_color("info"),
                    timestamp=datetime.utcnow(),
                )

                # Format value based on type
                if isinstance(current_value, bool):
                    formatted_value = "✅ Enabled" if current_value else "❌ Disabled"
                elif isinstance(current_value, (list, dict)):
                    formatted_value = (
                        f"```json\n{json.dumps(current_value, indent=2)}\n```"
                    )
                else:
                    formatted_value = str(current_value)

                embed.add_field(name="Value", value=formatted_value, inline=False)

                await interaction.response.send_message(embed=embed)
                return

            except (KeyError, TypeError):
                # Setting not found
                embed = discord.Embed(
                    title="❌ Setting Not Found",
                    description=f"The configuration setting `{setting}` was not found.",
                    color=self.config.get_color("error"),
                )

                # Suggest similar settings
                if "." in setting:
                    # For nested settings, suggest parent path
                    parent_path = ".".join(setting.split(".")[:-1])
                    try:
                        parent_value = guild_config
                        for key in parent_path.split("."):
                            parent_value = parent_value[key]

                        if isinstance(parent_value, dict):
                            embed.add_field(
                                name="Available Settings",
                                value=f"Available settings under `{parent_path}`:\n"
                                + "\n".join(
                                    [
                                        f"`{parent_path}.{key}`"
                                        for key in parent_value.keys()
                                    ]
                                ),
                                inline=False,
                            )
                    except (KeyError, TypeError):
                        pass

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        # Changing a setting
        try:
            # Parse value based on content
            if value.lower() in ("true", "yes", "enable", "enabled", "on", "1"):
                parsed_value = True
            elif value.lower() in ("false", "no", "disable", "disabled", "off", "0"):
                parsed_value = False
            elif value.lower() in ("null", "none"):
                parsed_value = None
            elif value.startswith("[") and value.endswith("]"):
                # Try to parse as list
                try:
                    parsed_value = json.loads(value)
                    if not isinstance(parsed_value, list):
                        parsed_value = value
                except:
                    parsed_value = value
            elif value.startswith("{") and value.endswith("}"):
                # Try to parse as dict
                try:
                    parsed_value = json.loads(value)
                    if not isinstance(parsed_value, dict):
                        parsed_value = value
                except:
                    parsed_value = value
            else:
                # Try to parse as integer
                try:
                    if value.isdigit():
                        parsed_value = int(value)
                    else:
                        parsed_value = float(value)
                except:
                    parsed_value = value

            # Set the value
            if self.config.set_guild_setting(guild_id, setting, parsed_value):
                embed = discord.Embed(
                    title="✅ Configuration Updated",
                    description=f"Successfully updated `{setting}`.",
                    color=self.config.get_color("success"),
                    timestamp=datetime.utcnow(),
                )

                embed.add_field(
                    name="Old Value",
                    value=str(self.config.get_guild_setting(guild_id, setting, "N/A")),
                    inline=True,
                )

                embed.add_field(name="New Value", value=str(parsed_value), inline=True)

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"❌ Failed to update the setting `{setting}`.", ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error updating configuration: {str(e)}", ephemeral=True
            )
            self.logger.error(f"Error updating config: {traceback.format_exc()}")

    @app_commands.command(name="shutdown", description="Shut down the bot")
    @app_commands.default_permissions(administrator=True)
    async def shutdown_command(self, interaction: discord.Interaction):
        """Shut down the bot (Owner only)"""
        # Check if user is bot owner
        app_info = await self.bot.application_info()
        is_owner = interaction.user.id == app_info.owner.id

        if not is_owner:
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner.", ephemeral=True
            )
            return

        # Create confirmation view
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.confirmed = False

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm(
                self,
                confirm_interaction: discord.Interaction,
                button: discord.ui.Button,
            ):
                self.confirmed = True
                self.stop()
                await confirm_interaction.response.edit_message(
                    content="✅ Shutting down...", embed=None, view=None
                )

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(
                self, cancel_interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.stop()
                await cancel_interaction.response.edit_message(
                    content="❌ Shutdown cancelled.", embed=None, view=None
                )

        # Show confirmation prompt
        view = ConfirmView()
        embed = discord.Embed(
            title="⚠️ Confirm Shutdown",
            description="Are you sure you want to shut down the bot?",
            color=self.config.get_color("warning"),
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        # Wait for response
        await view.wait()

        if view.confirmed:
            self.logger.info(f"Bot shutdown initiated by {interaction.user}")
            await self.bot.close()

    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (max 100)",
        user="Only delete messages from this user",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def purge_command(
        self,
        interaction: discord.Interaction,
        amount: int,
        user: Optional[discord.Member] = None,
    ):
        """Delete multiple messages (Mod only)"""
        # Check if user has permission
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", ephemeral=True
            )
            return

        # Check valid amount
        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "❌ Please specify a number between 1 and 100.", ephemeral=True
            )
            return

        # Need to defer immediately because purge can take time
        await interaction.response.defer(ephemeral=True)

        # Delete messages
        try:
            # Define a check for user filter if needed
            def check_messages(message):
                if user:
                    return message.author == user
                return True

            deleted = await interaction.channel.purge(
                limit=amount, check=check_messages, bulk=True
            )

            # Send completion message
            embed = discord.Embed(
                title="🗑️ Purge Complete",
                description=f"Successfully deleted **{len(deleted)}** message(s).",
                color=self.config.get_color("success"),
            )

            if user:
                embed.add_field(
                    name="Filter",
                    value=f"Messages from {user.mention} only",
                    inline=True,
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Add to audit log
            self.logger.info(
                f"Purge: {interaction.user} deleted {len(deleted)} messages in #{interaction.channel.name}"
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error deleting messages: {str(e)}", ephemeral=True
            )
            self.logger.error(f"Purge error: {traceback.format_exc()}")


async def setup(bot):
    await bot.add_cog(Admin(bot))
