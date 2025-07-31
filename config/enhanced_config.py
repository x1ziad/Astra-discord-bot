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

        if config_manager.is_channel_allowed(interaction.channel, feature_name):
            return True
        else:
            # Get the list of allowed channels
            guild_id = interaction.guild.id if interaction.guild else None
            allowed_channels = config_manager.get_allowed_channels(
                feature_name, guild_id
            )

            # If there are allowed channels, mention them
            if allowed_channels:
                channel_mentions = [
                    f"<#{channel_id}>" for channel_id in allowed_channels
                ]
                channels_text = ", ".join(channel_mentions)
                await interaction.response.send_message(
                    f"❌ This command can only be used in the following channels: {channels_text}",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"❌ This command can only be used in designated channels. Please ask an admin to set up channels for {feature_name}.",
                    ephemeral=True,
                )
            return False

    return app_commands.check(predicate)
