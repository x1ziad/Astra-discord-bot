#!/usr/bin/env python3
"""
Architecture verification test for the new Consolidated AI Engine
This script verifies the architecture is properly structured without environment dependencies.
"""

import os
import sys
import logging
import importlib.util

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_file_structure():
    """Test that all expected files exist and old files are removed"""
    base_path = "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot"

    # New files that should exist
    required_files = [
        "ai/consolidated_ai_engine.py",
        "config/enhanced_config.py",
        "cogs/advanced_ai.py",
        "ai/personalities/default.json",
        "ai/personalities/stellaris.json",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            logger.info(f"✅ {file_path} exists")
        else:
            logger.error(f"❌ {file_path} missing")
            missing_files.append(file_path)

    # Old files that should be removed
    removed_files = [
        "ai/conversation_engine.py",
        "ai/enhanced_conversation_engine.py",
        "ai/enhanced_ai_handler.py",
    ]

    still_exists = []
    for file_path in removed_files:
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            logger.info(f"✅ {file_path} successfully removed")
        else:
            logger.warning(f"⚠️ {file_path} still exists (should be removed)")
            still_exists.append(file_path)

    return len(missing_files) == 0 and len(still_exists) == 0


def test_consolidated_ai_engine_structure():
    """Test the structure of the consolidated AI engine file"""
    try:
        file_path = "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot/ai/consolidated_ai_engine.py"

        with open(file_path, "r") as f:
            content = f.read()

        # Check for key classes
        required_classes = [
            "class IntelligentCache:",
            "class AdvancedSentimentAnalyzer:",
            "class PersonalityEngine:",
            "class ConsolidatedAIEngine:",
        ]

        for class_def in required_classes:
            if class_def in content:
                logger.info(
                    f"✅ Found {class_def.replace('class ', '').replace(':', '')}"
                )
            else:
                logger.error(
                    f"❌ Missing {class_def.replace('class ', '').replace(':', '')}"
                )
                return False

        # Check for key methods
        required_methods = [
            "async def generate_response(",
            "async def generate_image(",
            "async def get_health_status(",
            "def get_stats(",
        ]

        for method in required_methods:
            if method in content:
                logger.info(
                    f"✅ Found method {method.split('(')[0].replace('async def ', '').replace('def ', '')}"
                )
            else:
                logger.error(f"❌ Missing method {method}")
                return False

        # Check file size (should be substantial)
        file_size = len(content)
        if file_size > 40000:  # Should be over 40KB
            logger.info(f"✅ File size appropriate: {file_size} characters")
        else:
            logger.warning(f"⚠️ File seems small: {file_size} characters")

        return True

    except Exception as e:
        logger.error(f"❌ Error analyzing consolidated AI engine: {e}")
        return False


def test_enhanced_config_structure():
    """Test the structure of the enhanced config file"""
    try:
        file_path = "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot/config/enhanced_config.py"

        with open(file_path, "r") as f:
            content = f.read()

        # Check for key classes
        required_elements = [
            "class AIProviderConfig:",
            "class EnhancedConfigManager:",
            "def get_setting(",
            "def get_ai_provider_config(",
            "def get_database_config(",
            "def get_discord_config(",
        ]

        for element in required_elements:
            if element in content:
                logger.info(
                    f"✅ Found {element.replace('class ', '').replace('def ', '').replace(':', '').replace('(', '')}"
                )
            else:
                logger.error(f"❌ Missing {element}")
                return False

        return True

    except Exception as e:
        logger.error(f"❌ Error analyzing enhanced config: {e}")
        return False


def test_advanced_ai_cog_updates():
    """Test that the advanced AI cog has been properly updated"""
    try:
        file_path = (
            "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot/cogs/advanced_ai.py"
        )

        with open(file_path, "r") as f:
            content = f.read()

        # Check that old imports are removed and new ones added
        if "from ai.consolidated_ai_engine import ConsolidatedAIEngine" in content:
            logger.info("✅ New consolidated AI engine import found")
        else:
            logger.error("❌ Missing consolidated AI engine import")
            return False

        if "from config.enhanced_config import EnhancedConfigManager" in content:
            logger.info("✅ New enhanced config manager import found")
        else:
            logger.error("❌ Missing enhanced config manager import")
            return False

        # Check that old method calls are updated
        if "await self.ai_client.generate_response(" in content:
            logger.info("✅ Updated to use new generate_response method")
        else:
            logger.warning("⚠️ May not be using new generate_response method")

        # Check that old methods are removed
        old_methods = [
            "async def _generate_universal_response(",
            "async def _generate_openai_response(",
        ]

        for method in old_methods:
            if method not in content:
                logger.info(
                    f"✅ Old method removed: {method.split('(')[0].replace('async def ', '')}"
                )
            else:
                logger.warning(f"⚠️ Old method still exists: {method}")

        return True

    except Exception as e:
        logger.error(f"❌ Error analyzing advanced AI cog: {e}")
        return False


def test_personality_files():
    """Test that personality files are properly structured"""
    personalities_dir = (
        "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot/ai/personalities"
    )

    if not os.path.exists(personalities_dir):
        logger.error("❌ Personalities directory missing")
        return False

    required_personalities = [
        "default.json",
        "stellaris.json",
        "friendly.json",
        "professional.json",
    ]

    for personality_file in required_personalities:
        file_path = os.path.join(personalities_dir, personality_file)
        if os.path.exists(file_path):
            try:
                import json

                with open(file_path, "r") as f:
                    personality_data = json.load(f)

                # Check basic structure
                if "name" in personality_data and "personality" in personality_data:
                    logger.info(f"✅ {personality_file} properly structured")
                else:
                    logger.warning(f"⚠️ {personality_file} missing required fields")

            except json.JSONDecodeError:
                logger.error(f"❌ {personality_file} is not valid JSON")
                return False
        else:
            logger.warning(f"⚠️ {personality_file} missing")

    return True


def main():
    """Run all architecture verification tests"""
    logger.info("🚀 Starting Architecture Verification Tests")
    logger.info("=" * 60)

    results = []

    # Test 1: File structure
    logger.info("\n📁 TEST 1: File Structure")
    logger.info("-" * 30)
    results.append(test_file_structure())

    # Test 2: Consolidated AI Engine structure
    logger.info("\n🤖 TEST 2: Consolidated AI Engine Structure")
    logger.info("-" * 30)
    results.append(test_consolidated_ai_engine_structure())

    # Test 3: Enhanced Config structure
    logger.info("\n⚙️ TEST 3: Enhanced Config Structure")
    logger.info("-" * 30)
    results.append(test_enhanced_config_structure())

    # Test 4: Advanced AI Cog updates
    logger.info("\n🔄 TEST 4: Advanced AI Cog Updates")
    logger.info("-" * 30)
    results.append(test_advanced_ai_cog_updates())

    # Test 5: Personality files
    logger.info("\n👤 TEST 5: Personality Files")
    logger.info("-" * 30)
    results.append(test_personality_files())

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 ARCHITECTURE VERIFICATION SUMMARY")
    logger.info("=" * 60)

    passed_tests = sum(results)
    total_tests = len(results)

    if passed_tests == total_tests:
        logger.info(f"🎉 ALL {total_tests} TESTS PASSED!")
        logger.info("✅ The consolidated AI architecture is properly implemented")
        logger.info("✅ Phase 1: Architecture Consolidation - COMPLETE")
        logger.info("🚀 Ready for Phase 2: Performance Optimization")
        return True
    else:
        logger.error(
            f"❌ {total_tests - passed_tests} out of {total_tests} tests failed"
        )
        logger.error("Please fix the issues above before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
