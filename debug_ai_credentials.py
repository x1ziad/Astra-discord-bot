"""
Debug AI Credentials Module
Simple utility to debug AI service configurations
"""

import os
import logging

logger = logging.getLogger(__name__)


def debug_ai_credentials():
    """Debug AI service credentials and configuration"""
    try:
        logger.info("🔍 Debugging AI Credentials Configuration")

        # Check environment variables
        credentials_status = {
            "DISCORD_TOKEN": bool(os.getenv("DISCORD_TOKEN")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
            "FREEPIK_API_KEY": bool(os.getenv("FREEPIK_API_KEY")),
            "NASA_API_KEY": bool(os.getenv("NASA_API_KEY")),
        }

        logger.info("📊 Credential Status:")
        for service, available in credentials_status.items():
            status = "✅ Available" if available else "❌ Missing"
            logger.info(f"  {service}: {status}")

        # Check critical services
        critical_missing = []
        if not credentials_status["DISCORD_TOKEN"]:
            critical_missing.append("DISCORD_TOKEN")

        if not any(
            [
                credentials_status["OPENAI_API_KEY"],
                credentials_status["OPENROUTER_API_KEY"],
            ]
        ):
            critical_missing.append("AI_API_KEY (OpenAI or OpenRouter)")

        if critical_missing:
            logger.warning(
                f"⚠️  Critical credentials missing: {', '.join(critical_missing)}"
            )
        else:
            logger.info("✅ All critical credentials available")

        # Recommendations
        recommendations = []
        if not credentials_status["FREEPIK_API_KEY"]:
            recommendations.append("Add FREEPIK_API_KEY for image generation")
        if not credentials_status["NASA_API_KEY"]:
            recommendations.append("Add NASA_API_KEY for space content features")

        if recommendations:
            logger.info("💡 Optional improvements:")
            for rec in recommendations:
                logger.info(f"  • {rec}")

        logger.info("🔍 AI credentials debug completed")

    except Exception as e:
        logger.error(f"Debug AI credentials failed: {e}")


if __name__ == "__main__":
    debug_ai_credentials()
