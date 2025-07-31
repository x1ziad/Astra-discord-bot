# Add this to the AstraBot class to handle clean shutdown


async def close(self) -> None:
    """Clean up resources before the bot exits"""
    self.logger.info("🔄 Bot is shutting down, cleaning up resources...")

    # Close HTTP sessions
    try:
        from utils.http_client import close_session

        await close_session()
    except Exception as e:
        self.logger.error(f"Error closing HTTP sessions: {e}")

    # Close database connections if any
    # ...

    self.logger.info("👋 Bot is shutting down...")
    # Call the parent close method to clean up Discord-related resources
    await super().close()
