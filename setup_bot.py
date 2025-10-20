#!/usr/bin/env python3
"""
AstraBot Quick Setup
Interactive setup for essential configuration
"""

import os
import sys
from pathlib import Path


def setup_discord_bot():
    """Help set up Discord bot configuration"""
    print("🤖 Discord Bot Setup")
    print("=" * 30)

    print("\n📋 To set up your Discord bot:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click 'New Application' and give it a name")
    print("3. Go to 'Bot' section on the left")
    print("4. Click 'Reset Token' and copy the token")
    print("5. Go to 'OAuth2' > 'General' and copy the Client ID")

    discord_token = input("\n🔑 Enter your Discord Bot Token: ").strip()
    if not discord_token:
        print("❌ Token cannot be empty")
        return None, None

    client_id = input("🆔 Enter your Discord Client ID: ").strip()
    if not client_id:
        print("❌ Client ID cannot be empty")
        return None, None

    return discord_token, client_id


def setup_ai_provider():
    """Help set up AI provider"""
    print("\n🧠 AI Provider Setup")
    print("=" * 25)

    print("\nChoose an AI provider (you can add more later):")
    print("1. OpenAI (Recommended - Paid)")
    print("2. Google Gemini (Free tier available)")
    print("3. GitHub Models (Free)")
    print("4. OpenRouter (Various models)")
    print("5. Skip for now")

    choice = input("\nEnter your choice (1-5): ").strip()

    if choice == "1":
        print("\n📋 OpenAI Setup:")
        print("1. Go to https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        api_key = input("🔑 Enter your OpenAI API Key: ").strip()
        return "OPENAI_API_KEY", api_key if api_key else None

    elif choice == "2":
        print("\n📋 Google Gemini Setup:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Create a new API key")
        api_key = input("🔑 Enter your Google API Key: ").strip()
        return "GOOGLE_API_KEY", api_key if api_key else None

    elif choice == "3":
        print("\n📋 GitHub Models Setup:")
        print("1. Go to https://github.com/settings/personal-access-tokens/tokens")
        print("2. Create a new token with 'model.request' permission")
        api_key = input("🔑 Enter your GitHub Token: ").strip()
        return "GITHUB_TOKEN", api_key if api_key else None

    elif choice == "4":
        print("\n📋 OpenRouter Setup:")
        print("1. Go to https://openrouter.ai/keys")
        print("2. Create a new API key")
        api_key = input("🔑 Enter your OpenRouter API Key: ").strip()
        return "OPENROUTER_API_KEY", api_key if api_key else None

    else:
        return None, None


def update_env_file(discord_token, client_id, ai_provider_key, ai_api_key):
    """Update .env file with configuration"""

    try:
        # Read current .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        # Update or add Discord configuration
        updated_lines = []
        discord_token_set = False
        client_id_set = False
        ai_key_set = False

        for line in lines:
            if line.startswith("DISCORD_TOKEN="):
                updated_lines.append(f"DISCORD_TOKEN={discord_token}\n")
                discord_token_set = True
            elif line.startswith("DISCORD_CLIENT_ID="):
                updated_lines.append(f"DISCORD_CLIENT_ID={client_id}\n")
                client_id_set = True
            elif ai_provider_key and line.startswith(f"{ai_provider_key}="):
                updated_lines.append(f"{ai_provider_key}={ai_api_key}\n")
                ai_key_set = True
            else:
                updated_lines.append(line)

        # Add missing configurations
        if not discord_token_set:
            updated_lines.append(f"DISCORD_TOKEN={discord_token}\n")
        if not client_id_set:
            updated_lines.append(f"DISCORD_CLIENT_ID={client_id}\n")
        if ai_provider_key and not ai_key_set:
            updated_lines.append(f"{ai_provider_key}={ai_api_key}\n")

        # Write updated .env file
        with open(env_file, "w") as f:
            f.writelines(updated_lines)

        print("✅ Configuration saved to .env file")
        return True

    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 AstraBot Quick Setup")
    print("=" * 30)

    # Check if we're in the right directory
    if not Path("bot.1.0.py").exists():
        print("❌ Error: bot.1.0.py not found")
        print("   Please run this script from the AstraBot directory")
        return

    # Discord bot setup
    discord_token, client_id = setup_discord_bot()
    if not discord_token or not client_id:
        print("❌ Discord bot setup incomplete")
        return

    # AI provider setup
    ai_provider_key, ai_api_key = setup_ai_provider()

    # Update .env file
    if update_env_file(discord_token, client_id, ai_provider_key, ai_api_key):
        print("\n🎉 Setup complete!")

        if ai_provider_key:
            print("✅ Discord bot configured")
            print("✅ AI provider configured")
            print("\n🚀 Ready to deploy! Run: ./deploy_local.sh")
        else:
            print("✅ Discord bot configured")
            print("⚠️  No AI provider configured")
            print("\n🔧 You can add AI providers later by editing .env file")
            print("   Or run this setup script again")

        # Show invite link
        print(f"\n🔗 Bot Invite Link:")
        print(
            f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands"
        )

    else:
        print("❌ Setup failed")


if __name__ == "__main__":
    main()
