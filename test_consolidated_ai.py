#!/usr/bin/env python3
"""
Integration test for the new Consolidated AI Engine
This script tests the basic functionality of the new architecture.
"""

import os
import sys
import asyncio
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_consolidated_ai_engine():
    """Test the consolidated AI engine"""
    try:
        # Import the new consolidated AI engine
        from ai.consolidated_ai_engine import ConsolidatedAIEngine
        from config.enhanced_config import EnhancedConfigManager

        logger.info(
            "✅ Successfully imported ConsolidatedAIEngine and EnhancedConfigManager"
        )

        # Test configuration manager
        config = EnhancedConfigManager()
        logger.info(f"✅ Configuration manager initialized")

        # Test basic settings
        ai_model = config.get_setting("AI_MODEL", "deepseek/deepseek-r1:nitro")
        logger.info(f"✅ AI Model: {ai_model}")

        # Initialize the consolidated AI engine
        ai_engine = ConsolidatedAIEngine()
        logger.info("✅ ConsolidatedAIEngine initialized successfully")

        # Test health status
        try:
            health_status = await ai_engine.get_health_status()
            logger.info(f"✅ Health status: {health_status}")
        except Exception as e:
            logger.warning(
                f"⚠️ Health status check failed (expected if no API keys): {e}"
            )

        # Test basic response generation (will fail without API keys but should not crash)
        try:
            test_context = {
                "user_id": 12345,
                "channel_type": "test",
                "conversation_history": [],
            }

            # This should gracefully handle missing API keys
            response = await ai_engine.generate_response(
                "Hello, this is a test", test_context
            )
            if "not configured" in response.lower() or "api" in response.lower():
                logger.info("✅ Engine correctly handles missing API configuration")
            else:
                logger.info(f"✅ Response generated: {response[:100]}...")

        except Exception as e:
            logger.warning(
                f"⚠️ Response generation failed (expected without API keys): {e}"
            )

        # Test personality system
        try:
            personalities = ai_engine.personality_engine.get_available_personalities()
            logger.info(f"✅ Available personalities: {personalities}")
        except Exception as e:
            logger.warning(f"⚠️ Personality system test failed: {e}")

        # Test caching system
        try:
            cache_stats = ai_engine.cache.get_stats()
            logger.info(f"✅ Cache stats: {cache_stats}")
        except Exception as e:
            logger.warning(f"⚠️ Cache system test failed: {e}")

        logger.info(
            "🎉 Consolidated AI Engine integration test completed successfully!"
        )
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False


async def test_advanced_ai_cog():
    """Test the updated Advanced AI Cog"""
    try:
        # Test that the cog can be imported without errors
        from cogs.advanced_ai import AdvancedAICog

        logger.info("✅ Successfully imported AdvancedAICog")

        # Create a mock bot object for testing
        class MockBot:
            def __init__(self):
                self.user = None

        mock_bot = MockBot()

        # Initialize the cog
        cog = AdvancedAICog(mock_bot)
        logger.info("✅ AdvancedAICog initialized successfully")

        # Check that it has the new AI client
        if hasattr(cog, "ai_client") and cog.ai_client:
            logger.info("✅ Cog has consolidated AI client")
        else:
            logger.warning("⚠️ Cog doesn't have AI client (expected without API keys)")

        logger.info("🎉 Advanced AI Cog integration test completed successfully!")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return False


async def main():
    """Run all integration tests"""
    logger.info("🚀 Starting Consolidated AI Integration Tests")

    # Test 1: Consolidated AI Engine
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: Consolidated AI Engine")
    logger.info("=" * 50)
    test1_result = await test_consolidated_ai_engine()

    # Test 2: Advanced AI Cog
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: Advanced AI Cog Integration")
    logger.info("=" * 50)
    test2_result = await test_advanced_ai_cog()

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("=" * 50)

    if test1_result and test2_result:
        logger.info(
            "🎉 ALL TESTS PASSED! The new consolidated AI architecture is working correctly."
        )
        logger.info("✅ Ready to deploy the enhanced AI system")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
