#!/usr/bin/env python3
"""
Test Universal AI Integration
Tests the universal AI client integration with Discord bot
"""

import asyncio
import os
import sys
import logging

# Add the project root to sys.path
sys.path.insert(0, "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot")

# Set environment variables for testing
os.environ["DISCORD_TOKEN"] = "dummy_token_for_testing"  # Required by railway config
os.environ["AI_API_KEY"] = (
    "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"
)
os.environ["AI_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["AI_MODEL"] = "deepseek/deepseek-r1:nitro"
os.environ["AI_PROVIDER"] = "universal"

# Import necessary modules
from ai.universal_ai_client import (
    UniversalAIClient,
    get_ai_client,
    initialize_ai_client,
)
from config.railway_config import get_railway_config


async def test_universal_ai_integration():
    """Test universal AI integration with Railway config"""
    print("🧪 Testing Universal AI Integration...")

    # Test 1: Railway Configuration
    print("\n1️⃣ Testing Railway Configuration...")
    try:
        railway_config = get_railway_config()
        universal_config = railway_config.get_universal_ai_config()

        print(
            f"   ✅ API Key: {'*' * 20 + universal_config['api_key'][-10:] if universal_config['api_key'] else 'None'}"
        )
        print(f"   ✅ Base URL: {universal_config['base_url']}")
        print(f"   ✅ Model: {universal_config['model']}")
        print(f"   ✅ Provider: {universal_config['provider_name']}")
        print(f"   ✅ Max Tokens: {universal_config['max_tokens']}")
        print(f"   ✅ Temperature: {universal_config['temperature']}")

    except Exception as e:
        print(f"   ❌ Railway config error: {e}")
        return False

    # Test 2: Universal AI Client Initialization
    print("\n2️⃣ Testing Universal AI Client Initialization...")
    try:
        client = UniversalAIClient(
            api_key=universal_config["api_key"],
            base_url=universal_config["base_url"],
            model=universal_config["model"],
            provider_name=universal_config["provider_name"],
        )

        print(f"   ✅ Client created: {client.is_available()}")
        print(f"   ✅ Provider: {client.provider_name}")
        print(f"   ✅ Model: {client.model}")
        print(f"   ✅ Endpoint: {client.base_url}")

    except Exception as e:
        print(f"   ❌ Client initialization error: {e}")
        return False

    # Test 3: Connection Test
    print("\n3️⃣ Testing API Connection...")
    try:
        connection_result = await client.test_connection()

        if connection_result["success"]:
            print(f"   ✅ Connection successful!")
            print(f"   ✅ Response: {connection_result['response']}")
        else:
            print(f"   ❌ Connection failed: {connection_result['error']}")
            return False

    except Exception as e:
        print(f"   ❌ Connection test error: {e}")
        return False

    # Test 4: Chat Completion
    print("\n4️⃣ Testing Chat Completion...")
    try:
        messages = [
            {"role": "system", "content": "You are Astra, a helpful AI assistant."},
            {"role": "user", "content": "Hello! Please introduce yourself briefly."},
        ]

        response = await client.chat_completion(messages)

        print(f"   ✅ Response received: {len(response.content)} characters")
        print(f"   ✅ Model used: {response.model}")
        print(f"   ✅ Provider: {response.provider}")
        print(f"   ✅ Tokens used: {response.tokens_used}")
        print(f"   ✅ Content preview: {response.content[:100]}")

    except Exception as e:
        print(f"   ❌ Chat completion error: {e}")
        return False

    # Test 5: DeepSeek R1 Reasoning Test
    print("\n5️⃣ Testing DeepSeek R1 Reasoning...")
    try:
        reasoning_prompt = "Please solve this step by step: What is 15 * 24? Show your thinking process."
        messages = [
            {
                "role": "system",
                "content": "You are a helpful math assistant. Show your step-by-step reasoning.",
            },
            {"role": "user", "content": reasoning_prompt},
        ]

        response = await client.chat_completion(messages)

        print(f"   ✅ Reasoning response: {len(response.content)} characters")
        print(f"   ✅ Content preview: {response.content[:200]}...")

        # Check if it contains step-by-step reasoning
        has_steps = any(
            word in response.content.lower()
            for word in ["step", "first", "then", "finally", "therefore"]
        )
        print(f"   ✅ Contains reasoning steps: {has_steps}")

    except Exception as e:
        print(f"   ❌ Reasoning test error: {e}")
        return False

    # Test 6: Global Client Test
    print("\n6️⃣ Testing Global Client Access...")
    try:
        # Initialize global client
        global_client = initialize_ai_client(
            api_key=universal_config["api_key"],
            base_url=universal_config["base_url"],
            model=universal_config["model"],
            provider_name=universal_config["provider_name"],
        )

        # Test global client
        global_response = await global_client.generate_text("Hello from global client!")

        print(f"   ✅ Global client response: {len(global_response)} characters")
        print(f"   ✅ Response preview: {global_response[:100]}")

    except Exception as e:
        print(f"   ❌ Global client error: {e}")
        return False

    # Test 7: Status Information
    print("\n7️⃣ Testing Status Information...")
    try:
        status = client.get_status()

        print(f"   ✅ Provider: {status['provider']}")
        print(f"   ✅ Available: {status['available']}")
        print(f"   ✅ Model: {status['model']}")
        print(f"   ✅ Endpoint: {status['endpoint']}")
        print(f"   ✅ Max Tokens: {status['max_tokens']}")
        print(f"   ✅ Temperature: {status['temperature']}")

    except Exception as e:
        print(f"   ❌ Status information error: {e}")
        return False

    print("\n🎉 Universal AI Integration Test Complete!")
    print("✅ All tests passed successfully!")
    print("🚀 The universal AI system is ready for Discord bot integration!")

    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the test
    success = asyncio.run(test_universal_ai_integration())

    if success:
        print("\n🎯 READY FOR DEPLOYMENT:")
        print("   • Set Railway environment variables:")
        print(
            "     - AI_API_KEY=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"
        )
        print("     - AI_BASE_URL=https://openrouter.ai/api/v1")
        print("     - AI_MODEL=deepseek/deepseek-r1:nitro")
        print("     - AI_PROVIDER=universal")
        print("   • Deploy to Railway")
        print("   • Test with /ai_status and /chat commands")
    else:
        print("\n❌ DEPLOYMENT BLOCKED:")
        print("   • Fix the errors shown above")
        print("   • Re-run this test before deploying")
        sys.exit(1)
