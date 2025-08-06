"""
Railway Environment Variables Verification Script
Check what's actually working vs what's missing
"""

import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_environment_variables():
    """Check all possible environment variable configurations"""

    print("🚄 RAILWAY ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)

    # All possible AI API variables
    ai_variables = {
        "AI_API_KEY": os.getenv("AI_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

    # Other important variables
    other_variables = {
        "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
        "FREEPIK_API_KEY": os.getenv("FREEPIK_API_KEY"),
        "NASA_API_KEY": os.getenv("NASA_API_KEY"),
        "AI_BASE_URL": os.getenv("AI_BASE_URL"),
        "AI_MODEL": os.getenv("AI_MODEL"),
    }

    print("🤖 AI CONVERSATION API VARIABLES:")
    ai_configured = False
    for var, value in ai_variables.items():
        if value:
            status = f"✅ {var}: {value[:10]}...{value[-4:]}"
            ai_configured = True
        else:
            status = f"❌ {var}: Not set"
        print(f"  {status}")

    print(
        f"\n🎯 AI Conversation Status: {'✅ CONFIGURED' if ai_configured else '❌ NOT CONFIGURED'}"
    )

    print("\n🔧 OTHER VARIABLES:")
    for var, value in other_variables.items():
        if value:
            if len(value) > 20:
                display_value = f"{value[:10]}...{value[-4:]}"
            else:
                display_value = value
            status = f"✅ {var}: {display_value}"
        else:
            status = f"❌ {var}: Not set"
        print(f"  {status}")

    # Analysis
    print("\n📊 ANALYSIS:")
    print(
        f"  Discord Bot: {'✅ Ready' if other_variables['DISCORD_TOKEN'] else '❌ Missing DISCORD_TOKEN'}"
    )
    print(
        f"  AI Conversation: {'✅ Ready' if ai_configured else '❌ Missing AI API key'}"
    )
    print(
        f"  Image Generation: {'✅ Ready' if other_variables['FREEPIK_API_KEY'] else '❌ Missing FREEPIK_API_KEY'}"
    )

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not ai_configured:
        print("  🔑 Set one of these AI API keys in Railway:")
        print("     • AI_API_KEY=your_openrouter_key")
        print("     • OPENROUTER_API_KEY=your_openrouter_key")
        print("     • OPENAI_API_KEY=your_openai_key")

    if not other_variables["FREEPIK_API_KEY"]:
        print("  🎨 Set FREEPIK_API_KEY for image generation")
        print("     • Get key at: https://www.freepik.com/api")

    if ai_configured and other_variables["FREEPIK_API_KEY"]:
        print("  🎉 All critical APIs configured - bot should work fully!")

    return ai_configured, bool(other_variables["FREEPIK_API_KEY"])


async def test_ai_systems():
    """Test the actual AI systems if available"""

    print("\n🧪 TESTING AI SYSTEMS:")
    print("-" * 30)

    try:
        # Test Freepik Image Client
        from ai.freepik_image_client import FreepikImageClient

        client = FreepikImageClient()
        status = await client.get_status()

        print(f"🎨 Freepik Image Client:")
        print(f"  Available: {'✅' if status['available'] else '❌'}")
        print(
            f"  API Key: {'✅ Configured' if status['api_key_configured'] else '❌ Missing'}"
        )

        if status["available"]:
            print("  🧪 Testing connection...")
            test_result = await client.test_connection()
            if test_result.get("success"):
                print("  ✅ Connection test successful!")
            else:
                print(f"  ❌ Connection failed: {test_result.get('message')}")

        await client.close()

    except Exception as e:
        print(f"  ❌ Freepik test failed: {e}")

    try:
        # Test Universal AI Client
        from ai.universal_ai_client import UniversalAIClient

        client = UniversalAIClient()
        print(f"\n🤖 Universal AI Client:")
        print(f"  Available: {'✅' if client.is_available() else '❌'}")

        if client.is_available():
            print("  🧪 Testing connection...")
            test_result = await client.test_connection()
            if test_result.get("success"):
                print("  ✅ AI conversation test successful!")
            else:
                print(f"  ❌ AI test failed: {test_result.get('error')}")

    except Exception as e:
        print(f"  ❌ Universal AI test failed: {e}")


def main():
    """Main verification function"""

    # Check environment variables
    ai_configured, image_configured = check_environment_variables()

    # Test systems if available
    if ai_configured or image_configured:
        print("\n" + "=" * 60)
        asyncio.run(test_ai_systems())

    print("\n" + "=" * 60)
    print("🎯 VERIFICATION COMPLETE")

    if ai_configured and image_configured:
        print("🎉 All systems configured - your bot should work perfectly!")
    elif image_configured:
        print("🎨 Image generation ready - add AI API key for conversations")
    elif ai_configured:
        print("🤖 AI conversations ready - add FREEPIK_API_KEY for images")
    else:
        print("⚠️  Set up environment variables in Railway to enable features")


if __name__ == "__main__":
    main()
