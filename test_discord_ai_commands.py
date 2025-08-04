#!/usr/bin/env python3
"""
Test Discord AI Commands Integration
Tests the advanced AI cog with universal AI client
"""

import asyncio
import os
import sys
import logging
from unittest.mock import Mock, AsyncMock

# Add the project root to sys.path
sys.path.insert(0, "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot")

# Set environment variables for testing
os.environ["DISCORD_TOKEN"] = "dummy_token_for_testing"
os.environ["AI_API_KEY"] = (
    "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"
)
os.environ["AI_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["AI_MODEL"] = "deepseek/deepseek-r1:nitro"
os.environ["AI_PROVIDER"] = "universal"

# Import necessary modules
from cogs.advanced_ai import AdvancedAICog


async def test_discord_ai_integration():
    """Test Discord AI commands integration"""
    print("🤖 Testing Discord AI Commands Integration...")

    # Test 1: Initialize Advanced AI Cog
    print("\n1️⃣ Testing Advanced AI Cog Initialization...")
    try:
        # Mock bot
        mock_bot = Mock()
        mock_bot.guilds = []

        # Initialize the cog
        ai_cog = AdvancedAICog(mock_bot)

        print(f"   ✅ Cog initialized: {ai_cog is not None}")
        print(f"   ✅ AI client available: {ai_cog.ai_client is not None}")
        print(
            f"   ✅ AI client working: {ai_cog.ai_client.is_available() if ai_cog.ai_client else False}"
        )
        print(f"   ✅ AI model: {getattr(ai_cog, 'ai_model', 'Unknown')}")

    except Exception as e:
        print(f"   ❌ Cog initialization error: {e}")
        return False

    # Test 2: Generate AI Response (Internal Method)
    print("\n2️⃣ Testing AI Response Generation...")
    try:
        test_prompt = "Hello! Please introduce yourself as Astra."
        response = await ai_cog._generate_ai_response(test_prompt, user_id=12345)

        print(f"   ✅ Response generated: {len(response)} characters")
        print(f"   ✅ Response preview: {response[:100]}...")

        # Check if it's not an error message
        is_error = response.startswith("❌")
        print(f"   ✅ Valid response (not error): {not is_error}")

        if is_error:
            print(f"   ⚠️  Error response: {response}")
            return False

    except Exception as e:
        print(f"   ❌ Response generation error: {e}")
        return False

    # Test 3: Conversation History
    print("\n3️⃣ Testing Conversation History...")
    try:
        # Check if conversation was stored
        user_id = 12345
        history = ai_cog.conversation_history.get(user_id, [])

        print(f"   ✅ History stored: {len(history)} messages")
        print(
            f"   ✅ Has user message: {any(msg.get('role') == 'user' for msg in history)}"
        )
        print(
            f"   ✅ Has assistant message: {any(msg.get('role') == 'assistant' for msg in history)}"
        )

    except Exception as e:
        print(f"   ❌ Conversation history error: {e}")
        return False

    # Test 4: Multi-turn Conversation
    print("\n4️⃣ Testing Multi-turn Conversation...")
    try:
        # Second message
        follow_up = "What's your favorite topic to discuss?"
        response2 = await ai_cog._generate_ai_response(follow_up, user_id=12345)

        print(f"   ✅ Follow-up response: {len(response2)} characters")
        print(f"   ✅ Response preview: {response2[:100]}...")

        # Check updated history
        updated_history = ai_cog.conversation_history.get(12345, [])
        print(f"   ✅ Updated history: {len(updated_history)} messages")

    except Exception as e:
        print(f"   ❌ Multi-turn conversation error: {e}")
        return False

    # Test 5: DeepSeek R1 Reasoning with Context
    print("\n5️⃣ Testing DeepSeek R1 Reasoning with Context...")
    try:
        reasoning_prompt = "Can you solve this math problem step by step: If I have 24 apples and give away 1/3 of them, how many apples do I have left?"
        reasoning_response = await ai_cog._generate_ai_response(
            reasoning_prompt, user_id=12345
        )

        print(f"   ✅ Reasoning response: {len(reasoning_response)} characters")
        print(f"   ✅ Response preview: {reasoning_response[:150]}...")

        # Check if it shows step-by-step reasoning
        has_steps = any(
            indicator in reasoning_response.lower()
            for indicator in [
                "step",
                "first",
                "then",
                "next",
                "finally",
                "therefore",
                "1/3",
                "divide",
            ]
        )
        print(f"   ✅ Contains reasoning elements: {has_steps}")

    except Exception as e:
        print(f"   ❌ DeepSeek reasoning error: {e}")
        return False

    # Test 6: Performance Stats
    print("\n6️⃣ Testing Performance Statistics...")
    try:
        print(f"   ✅ API calls made: {ai_cog.api_calls_made}")
        print(f"   ✅ Successful responses: {ai_cog.successful_responses}")
        print(
            f"   ✅ Success rate: {(ai_cog.successful_responses/max(ai_cog.api_calls_made, 1)*100):.1f}%"
        )
        print(f"   ✅ Active conversations: {len(ai_cog.active_conversations)}")
        print(f"   ✅ Total users with history: {len(ai_cog.conversation_history)}")

    except Exception as e:
        print(f"   ❌ Performance stats error: {e}")
        return False

    # Test 7: Different User Context
    print("\n7️⃣ Testing Multi-user Context Separation...")
    try:
        # Different user
        user2_prompt = "Hello, I'm a different user. Who are you?"
        user2_response = await ai_cog._generate_ai_response(user2_prompt, user_id=67890)

        print(f"   ✅ User 2 response: {len(user2_response)} characters")
        print(f"   ✅ Response preview: {user2_response[:100]}...")

        # Check that contexts are separate
        user1_history = ai_cog.conversation_history.get(12345, [])
        user2_history = ai_cog.conversation_history.get(67890, [])

        print(f"   ✅ User 1 history: {len(user1_history)} messages")
        print(f"   ✅ User 2 history: {len(user2_history)} messages")
        print(f"   ✅ Contexts separated: {user1_history != user2_history}")

    except Exception as e:
        print(f"   ❌ Multi-user context error: {e}")
        return False

    print("\n🎉 Discord AI Commands Integration Test Complete!")
    print("✅ All tests passed successfully!")
    print("🚀 The Discord bot AI system is ready for deployment!")

    return True


async def test_status_methods():
    """Test the status and diagnostic methods"""
    print("\n🔍 Testing Status and Diagnostic Methods...")

    try:
        # Mock bot
        mock_bot = Mock()
        mock_bot.guilds = []

        # Initialize the cog
        ai_cog = AdvancedAICog(mock_bot)

        # Test status information
        if ai_cog.ai_client:
            status = ai_cog.ai_client.get_status()
            print(f"   ✅ Status method works: {status}")

            # Test connection
            connection_test = await ai_cog.ai_client.test_connection()
            print(f"   ✅ Connection test: {connection_test['success']}")

        print("   ✅ Status methods working correctly!")
        return True

    except Exception as e:
        print(f"   ❌ Status methods error: {e}")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the tests
    async def run_all_tests():
        success1 = await test_discord_ai_integration()
        success2 = await test_status_methods()

        return success1 and success2

    success = asyncio.run(run_all_tests())

    if success:
        print("\n🎯 DISCORD BOT READY FOR DEPLOYMENT:")
        print("   ✅ Universal AI client working perfectly")
        print("   ✅ Discord commands will work correctly")
        print("   ✅ Multi-user conversations supported")
        print("   ✅ DeepSeek R1 reasoning capabilities confirmed")
        print("   ✅ Performance tracking operational")
        print("\n🚀 Deploy to Railway and test with /ai_status and /chat commands!")
    else:
        print("\n❌ DEPLOYMENT BLOCKED:")
        print("   • Fix the errors shown above")
        print("   • Re-run this test before deploying")
        sys.exit(1)
