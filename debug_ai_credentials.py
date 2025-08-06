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

        # Check environment variables - comprehensive list
        credentials_status = {
            "DISCORD_TOKEN": bool(os.getenv("DISCORD_TOKEN")),
            # AI Conversation APIs (multiple possible variable names)
            "AI_API_KEY": bool(os.getenv("AI_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
            # Image Generation API
            "FREEPIK_API_KEY": bool(os.getenv("FREEPIK_API_KEY")),
            # Optional APIs
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

        # Check AI conversation API (any of these should work)
        ai_apis_available = any([
            credentials_status["AI_API_KEY"],
            credentials_status["OPENAI_API_KEY"], 
            credentials_status["OPENROUTER_API_KEY"],
        ])
        
        if not ai_apis_available:
            critical_missing.append("AI_API_KEY (OpenAI or OpenRouter)")

        if critical_missing:
            logger.warning(
                f"⚠️  Critical credentials missing: {', '.join(critical_missing)}"
            )
        else:
            logger.info("✅ All critical credentials available")

        # Enhanced recommendations with specific setup instructions
        recommendations = []
        
        # AI API recommendations
        if not ai_apis_available:
            recommendations.append("Set AI_API_KEY=your_openrouter_key OR OPENROUTER_API_KEY=your_key")
            recommendations.append("Get OpenRouter key at: https://openrouter.ai/keys")
        
        # Image generation recommendation
        if not credentials_status["FREEPIK_API_KEY"]:
            recommendations.append("Add FREEPIK_API_KEY for image generation")
            recommendations.append("Get Freepik key at: https://www.freepik.com/api")
        
        # Optional features
        if not credentials_status["NASA_API_KEY"]:
            recommendations.append("Add NASA_API_KEY for space content features")

        if recommendations:
            logger.info("💡 Setup recommendations:")
            for rec in recommendations:
                logger.info(f"  • {rec}")
        
        # Current configuration summary
        logger.info("🔧 Current Configuration:")
        logger.info(f"  Discord Bot: {'✅ Ready' if credentials_status['DISCORD_TOKEN'] else '❌ Not configured'}")
        logger.info(f"  AI Conversation: {'✅ Ready' if ai_apis_available else '❌ Not configured'}")
        logger.info(f"  Image Generation: {'✅ Ready' if credentials_status['FREEPIK_API_KEY'] else '❌ Not configured'}")
        
        logger.info("🔍 AI credentials debug completed")

    except Exception as e:
        logger.error(f"Debug AI credentials failed: {e}")


if __name__ == "__main__":
    debug_ai_credentials()
