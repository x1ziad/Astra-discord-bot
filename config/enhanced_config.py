"""
Adapter module for backward compatibility
Allows cogs to import from the old path while using the new config system
"""

from config.config_manager import config_manager


def feature_enabled(feature_path):
    """Decorator that checks if a feature is enabled"""
    from discord import app_commands

    async def predicate(interaction):
        if config_manager.is_feature_enabled(feature_path):
            return True
        else:
            await interaction.response.send_message(
                f"❌ The {feature_path.replace('.', ' ')} feature is currently disabled.",
                ephemeral=True,
            )
            return False

    return app_commands.check(predicate)


def channel_only(feature_name):
    """Decorator that restricts commands to specific channels"""
    from discord import app_commands

    async def predicate(interaction):
        # Check if the channel is allowed for this feature
        if not interaction.guild or not interaction.channel:
            return True  # Allow in DMs or when channel is None

        # Get the channel ID for this feature
        guild_id = interaction.guild.id if interaction.guild else None
        channel_id = config_manager.get_guild_setting(
            guild_id, f"channels.{feature_name}_channel"
        )

        # If no channel is configured, allow anywhere
        if not channel_id:
            return True

        # Check if current channel matches configured channel
        if str(interaction.channel.id) == str(channel_id):
            return True
        else:
            # Tell user where to use the command
            await interaction.response.send_message(
                f"❌ This command can only be used in <#{channel_id}>", ephemeral=True
            )
            return False

    return app_commands.check(predicate)
