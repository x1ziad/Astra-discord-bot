"""Utility functions for Astra bot"""

# Safe imports that won't fail
try:
    from utils.http_client import get_session, close_session
except ImportError:
    # Will be created later if missing
    pass

# Import checks if available, but don't fail if there are issues
try:
    from utils.checks import (
        feature_enabled,
        guild_admin_only,
        bot_owner_only,
        channel_only,
        cooldown,
    )
except ImportError:
    pass
except Exception as e:
    import logging

    logging = logging.getLogger("Astra")
    logging.error(f"Error importing utility functions: {e}")
