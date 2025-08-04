#!/usr/bin/env python3
"""
Quick script to verify and fix Railway environment variables
"""
import os


def check_env_vars():
    print("🔍 Checking current environment variables:")

    # Check all AI-related variables
    ai_vars = {
        "AI_API_KEY": "YOUR_OPENROUTER_API_KEY_HERE",
        "AI_BASE_URL": "https://openrouter.ai/api/v1",
        "AI_MODEL": "deepseek/deepseek-r1:nitro",
        "AI_PROVIDER": "universal",
    }

    all_good = True

    for var_name, expected_value in ai_vars.items():
        current_value = os.environ.get(var_name)

        if current_value is None:
            print(f"❌ {var_name}: NOT SET")
            all_good = False
        elif current_value == expected_value:
            print(f"✅ {var_name}: CORRECT")
        else:
            print(f"⚠️  {var_name}: INCORRECT")
            print(f"   Expected: {expected_value}")
            print(f"   Current:  {current_value}")
            all_good = False

    return all_good


def print_railway_commands():
    print("\n🚀 Railway CLI commands to fix environment variables:")
    print("Run these commands in your terminal:")
    print()
    print('railway variables set AI_API_KEY="YOUR_OPENROUTER_API_KEY_HERE"')
    print('railway variables set AI_BASE_URL="https://openrouter.ai/api/v1"')
    print('railway variables set AI_MODEL="deepseek/deepseek-r1:nitro"')
    print('railway variables set AI_PROVIDER="universal"')
    print()
    print("Then redeploy:")
    print("railway up")


if __name__ == "__main__":
    if check_env_vars():
        print("\n🎉 All environment variables are correct!")
    else:
        print_railway_commands()
