#!/usr/bin/env python3
"""
Comprehensive AI Parameter Testing Script
Tests all AI functionality and parameter compatibility
"""

import asyncio
import sys
import os
import json
import inspect
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine, get_engine
    from cogs.advanced_ai import AdvancedAI
    from config.enhanced_config import EnhancedConfigManager
    from config.config_manager import config_manager

    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class MockBot:
    """Mock bot for testing"""

    def __init__(self):
        self.logger = MockLogger()


class MockLogger:
    """Mock logger for testing"""

    def info(self, msg):
        print(f"INFO: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")

    def warning(self, msg):
        print(f"WARNING: {msg}")


class MockMessage:
    """Mock Discord message for testing"""

    def __init__(self, content, user_id, guild_id=None, channel_id=None):
        self.content = content
        self.author = MockUser(user_id)
        self.guild = MockGuild(guild_id) if guild_id else None
        self.channel = MockChannel(channel_id or 123456789)


class MockUser:
    """Mock Discord user"""

    def __init__(self, user_id):
        self.id = user_id


class MockGuild:
    """Mock Discord guild"""

    def __init__(self, guild_id):
        self.id = guild_id


class MockChannel:
    """Mock Discord channel"""

    def __init__(self, channel_id):
        self.id = channel_id


class MockInteraction:
    """Mock Discord interaction"""

    def __init__(self, user_id, guild_id=None, channel_id=None):
        self.user = MockUser(user_id)
        self.guild = MockGuild(guild_id) if guild_id else None
        self.channel = MockChannel(channel_id or 123456789)


async def test_ai_engine_direct():
    """Test the ConsolidatedAIEngine directly"""
    print("\n🧪 Testing ConsolidatedAIEngine Direct Access")
    print("=" * 50)

    try:
        # Test engine initialization
        engine = ConsolidatedAIEngine()
        print("✅ ConsolidatedAIEngine initialized")

        # Test method signature
        sig = inspect.signature(engine.process_conversation)
        print(f"✅ Method signature: {sig}")

        # Test basic conversation
        test_user_id = 1115739214148026469  # Your Discord ID
        test_guild_id = 1399956513745014967  # Your Stellaris server ID
        test_channel_id = 123456789

        print(f"Testing with parameters:")
        print(f"  - user_id: {test_user_id}")
        print(f"  - guild_id: {test_guild_id}")
        print(f"  - channel_id: {test_channel_id}")

        context_data = {"channel_type": "discord", "conversation_history": []}

        response = await engine.process_conversation(
            "Hello, this is a test message",
            user_id=test_user_id,
            guild_id=test_guild_id,
            channel_id=test_channel_id,
            context_data=context_data,
        )

        print(f"✅ AI Response received: {response[:100]}...")
        return True

    except Exception as e:
        print(f"❌ Direct engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_advanced_ai_cog():
    """Test the AdvancedAI cog"""
    print("\n🧪 Testing AdvancedAI Cog")
    print("=" * 50)

    try:
        # Initialize mock bot and cog
        bot = MockBot()
        ai_cog = AdvancedAI(bot)

        print("✅ AdvancedAI cog initialized")

        # Test method signature
        sig = inspect.signature(ai_cog._generate_ai_response)
        print(f"✅ _generate_ai_response signature: {sig}")

        # Test the AI response generation
        test_user_id = 1115739214148026469
        test_guild_id = 1399956513745014967
        test_channel_id = 123456789

        response = await ai_cog._generate_ai_response(
            "Test message for cog",
            user_id=test_user_id,
            guild_id=test_guild_id,
            channel_id=test_channel_id,
        )

        print(f"✅ Cog AI response: {response[:100]}...")
        return True

    except Exception as e:
        print(f"❌ AdvancedAI cog test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_message_processing():
    """Test message processing workflow"""
    print("\n🧪 Testing Message Processing Workflow")
    print("=" * 50)

    try:
        bot = MockBot()
        ai_cog = AdvancedAI(bot)

        # Create mock message
        message = MockMessage(
            content="Test conversation message",
            user_id=1115739214148026469,
            guild_id=1399956513745014967,
            channel_id=123456789,
        )

        print("✅ Mock message created")

        # Test the private conversation processing method
        # Note: This tests the internal logic without Discord API calls
        response = await ai_cog._generate_ai_response(
            message.content,
            user_id=message.author.id,
            guild_id=message.guild.id if message.guild else None,
            channel_id=message.channel.id,
        )

        print(f"✅ Message processing successful: {response[:100]}...")
        return True

    except Exception as e:
        print(f"❌ Message processing test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration and setup"""
    print("\n🧪 Testing Configuration")
    print("=" * 50)

    try:
        # Test config loading
        with open("config/config.json", "r") as f:
            config = json.load(f)

        print("✅ Configuration loaded successfully")
        print(f"  - Owner ID: {config.get('owner_id')}")
        print(f"  - AI Enabled: {config.get('ai_enabled')}")
        print(f"  - AI Personality: {config.get('ai_personality')}")
        print(f"  - AI Temperature: {config.get('ai_temperature')}")
        print(f"  - AI Max Tokens: {config.get('ai_max_tokens')}")

        # Test enhanced config manager
        enhanced_config = EnhancedConfigManager()
        owner_id = enhanced_config.get_owner_id()
        print(f"  - Enhanced Config Owner ID: {owner_id}")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_parameter_compatibility():
    """Test all parameter combinations"""
    print("\n🧪 Testing Parameter Compatibility")
    print("=" * 50)

    test_cases = [
        {
            "name": "Full parameters",
            "user_id": 1115739214148026469,
            "guild_id": 1399956513745014967,
            "channel_id": 123456789,
            "context_data": {"channel_type": "discord", "conversation_history": []},
        },
        {
            "name": "No guild (DM)",
            "user_id": 1115739214148026469,
            "guild_id": None,
            "channel_id": 987654321,
            "context_data": {"channel_type": "discord", "conversation_history": []},
        },
        {
            "name": "Minimal parameters",
            "user_id": 1115739214148026469,
            "guild_id": None,
            "channel_id": None,
            "context_data": None,
        },
    ]

    engine = ConsolidatedAIEngine()
    success_count = 0

    for i, case in enumerate(test_cases, 1):
        try:
            print(f"\nTest Case {i}: {case['name']}")

            response = await engine.process_conversation(
                f"Test message {i}",
                user_id=case["user_id"],
                guild_id=case["guild_id"],
                channel_id=case["channel_id"],
                context_data=case["context_data"],
            )

            print(f"✅ Success: {response[:50]}...")
            success_count += 1

        except Exception as e:
            print(f"❌ Failed: {e}")

    print(
        f"\n📊 Parameter Compatibility: {success_count}/{len(test_cases)} tests passed"
    )
    return success_count == len(test_cases)


async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive AI Parameter Tests")
    print("=" * 60)

    tests = [
        ("Configuration", test_configuration),
        ("AI Engine Direct", test_ai_engine_direct),
        ("AdvancedAI Cog", test_advanced_ai_cog),
        ("Message Processing", test_message_processing),
        ("Parameter Compatibility", test_parameter_compatibility),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n⏳ Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n📊 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your AI system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
