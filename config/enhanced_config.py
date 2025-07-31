# config/enhanced_config.py
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
