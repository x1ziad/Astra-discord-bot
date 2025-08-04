#!/usr/bin/env python3
"""
Railway Environment Variable Diagnostic
This script helps debug environment variable issues on Railway
"""

import os
import logging


def diagnose_environment():
    """Diagnose Railway environment variables"""
    print("🔍 RAILWAY ENVIRONMENT DIAGNOSTIC")
    print("=" * 50)

    # Check all AI-related environment variables
    env_vars = {
        "AI_API_KEY": os.getenv("AI_API_KEY"),
        "AI_BASE_URL": os.getenv("AI_BASE_URL"),
        "AI_MODEL": os.getenv("AI_MODEL"),
        "AI_PROVIDER": os.getenv("AI_PROVIDER"),
        "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),  # Legacy fallback
    }

    print("\n📋 Environment Variables:")
    for key, value in env_vars.items():
        if value:
            if "TOKEN" in key or "KEY" in key:
                # Hide sensitive values but show they exist
                masked_value = (
                    f"{'*' * 10}{value[-10:]}" if len(value) > 10 else "***HIDDEN***"
                )
                print(f"   ✅ {key}: {masked_value}")
            else:
                print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ {key}: NOT SET")

    # Check Railway-specific variables
    railway_vars = {
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
        "PORT": os.getenv("PORT"),
    }

    print("\n🚂 Railway Variables:")
    for key, value in railway_vars.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value or 'NOT SET'}")

    # Priority check for AI credentials
    print("\n🔑 AI Credentials Priority Check:")
    ai_key = env_vars.get("AI_API_KEY") or env_vars.get("OPENROUTER_API_KEY")
    if ai_key:
        print(f"   ✅ Found AI API Key: {'*' * 10}{ai_key[-10:]}")

        # Test key format
        if ai_key.startswith("sk-or-v1-"):
            print("   ✅ OpenRouter API key format detected")
        elif ai_key.startswith("sk-"):
            print("   ✅ OpenAI-compatible API key format detected")
        else:
            print("   ⚠️  Unknown API key format")
    else:
        print("   ❌ NO AI API KEY FOUND!")

    # Configuration validation
    print("\n⚙️ Configuration Validation:")
    base_url = env_vars.get("AI_BASE_URL", "https://api.openai.com/v1")
    model = env_vars.get("AI_MODEL", "gpt-3.5-turbo")
    provider = env_vars.get("AI_PROVIDER", "universal")

    print(f"   📡 Base URL: {base_url}")
    print(f"   🤖 Model: {model}")
    print(f"   🏭 Provider: {provider}")

    # Recommendations
    print("\n💡 Recommendations:")
    if not ai_key:
        print("   🚨 CRITICAL: Set AI_API_KEY environment variable on Railway")
        print(
            "   📝 Value: YOUR_OPENROUTER_API_KEY_HERE"
        )

    if not env_vars.get("AI_BASE_URL"):
        print("   ⚠️  Set AI_BASE_URL=https://openrouter.ai/api/v1")

    if not env_vars.get("AI_MODEL"):
        print("   ⚠️  Set AI_MODEL=deepseek/deepseek-r1:nitro")

    if not env_vars.get("AI_PROVIDER"):
        print("   ⚠️  Set AI_PROVIDER=universal")

    print("\n" + "=" * 50)
    print("📋 Copy this to Railway environment variables:")
    print(
        "AI_API_KEY=YOUR_OPENROUTER_API_KEY_HERE"
    )
    print("AI_BASE_URL=https://openrouter.ai/api/v1")
    print("AI_MODEL=deepseek/deepseek-r1:nitro")
    print("AI_PROVIDER=universal")


if __name__ == "__main__":
    diagnose_environment()
