#!/usr/bin/env python3
"""
Quick TARS and AI Companion Test
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_tars():
    """Test TARS personality engine"""
    try:
        from ai.tars_personality_engine import TARSPersonalityCore

        print("✅ TARS import successful")

        tars = TARSPersonalityCore()
        print("✅ TARS initialization successful")

        # Test basic response
        tars_response = tars.get_personality_response(
            context="Test conversation",
            user_input="Who are you?",
            response_type="identity",
        )
        response = tars_response.get("response") if tars_response else None

        if response:
            print(f"✅ TARS Response: {response[:100]}...")
            return True
        else:
            print("❌ TARS returned no response")
            return False

    except Exception as e:
        print(f"❌ TARS test failed: {e}")
        return False


async def test_ai_companion():
    """Test AI Companion import"""
    try:
        from cogs.ai_companion import AICompanion

        print("✅ AI Companion import successful")
        return True
    except Exception as e:
        print(f"❌ AI Companion test failed: {e}")
        return False


async def test_message_handling():
    """Test basic message handling components"""
    try:
        from cogs.ai_companion import AICompanion
        from ai.tars_personality_engine import TARSPersonalityCore

        # Simulate a basic test
        tars = TARSPersonalityCore()
        tars_response = tars.get_personality_response(
            context="DM conversation",
            user_input="Hello Astra, can you hear me?",
            response_type="conversation",
        )
        response = tars_response.get("response") if tars_response else None

        if response:
            print(f"✅ Message handling test: {response[:80]}...")
            return True
        else:
            print("❌ Message handling test failed")
            return False

    except Exception as e:
        print(f"❌ Message handling test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 ASTRA BOT QUICK VALIDATION")
    print("=" * 40)

    tests = [
        ("TARS Engine", test_tars),
        ("AI Companion", test_ai_companion),
        ("Message Handling", test_message_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} error: {e}")

    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🏆 ALL TESTS PASSED! Astra is ready to respond!")
    elif passed >= total * 0.75:
        print("✅ Most tests passed. System should work with minor issues.")
    else:
        print("❌ Multiple failures. System needs attention.")

    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(main())
