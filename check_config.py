#!/usr/bin/env python3
"""
AstraBot Configuration Checker
Helps verify your local deployment setup
"""

import os
import sys
from pathlib import Path


def check_configuration():
    """Check if AstraBot is properly configured for local deployment"""

    print("🔍 AstraBot Configuration Checker")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("bot.1.0.py").exists():
        print("❌ Error: bot.1.0.py not found")
        print("   Please run this script from the AstraBot directory")
        return False

    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("   Run: cp config/.env.template .env")
        print("   Then edit .env with your API keys")
        return False

    print("✅ Found .env file")

    # Load environment variables
    try:
        with open(".env", "r") as f:
            env_content = f.read()

        # Check for Discord token
        discord_configured = False
        ai_configured = False

        lines = env_content.split("\n")
        for line in lines:
            if (
                line.startswith("DISCORD_TOKEN=")
                and "your_discord_bot_token_here" not in line
                and line.strip() != "DISCORD_TOKEN="
            ):
                discord_configured = True
                print("✅ Discord token configured")
                break

        if not discord_configured:
            print("❌ Discord token not configured")
            print("   Please set DISCORD_TOKEN in .env file")

        # Check for AI providers
        ai_providers = {
            "OPENAI_API_KEY": "OpenAI",
            "GOOGLE_API_KEY": "Google Gemini",
            "OPENROUTER_API_KEY": "OpenRouter",
            "MISTRAL_API_KEY": "Mistral AI",
            "GITHUB_TOKEN": "GitHub Models",
        }

        configured_providers = []
        for key, name in ai_providers.items():
            for line in lines:
                if (
                    line.startswith(f"{key}=")
                    and f"your_{key.lower()}" not in line
                    and line.strip() != f"{key}="
                ):
                    configured_providers.append(name)
                    ai_configured = True
                    break

        if configured_providers:
            print(f"✅ AI providers configured: {', '.join(configured_providers)}")
        else:
            print("❌ No AI providers configured")
            print("   Please set at least one AI API key in .env file")

        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print(
                f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (compatible)"
            )
        else:
            print(
                f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)"
            )
            return False

        # Check directories
        required_dirs = ["data", "logs"]
        for directory in required_dirs:
            if Path(directory).exists():
                print(f"✅ {directory}/ directory exists")
            else:
                print(
                    f"⚠️  {directory}/ directory missing (will be created automatically)"
                )

        # Check requirements.txt
        if Path("requirements.txt").exists():
            print("✅ requirements.txt found")
        else:
            print("❌ requirements.txt not found")
            return False

        # Final assessment
        print("\n" + "=" * 40)

        if discord_configured and ai_configured:
            print("🎉 Configuration looks good!")
            print("Ready to deploy locally with: ./deploy_local.sh")
            return True
        else:
            print("⚠️  Configuration incomplete")
            print("Please fix the issues above before deploying")
            return False

    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False


def show_next_steps():
    """Show next steps for deployment"""
    print("\n📋 Next Steps:")
    print("1. Fix any configuration issues above")
    print("2. Run: ./deploy_local.sh")
    print("3. Bot will start and run continuously")
    print("4. Press Ctrl+C to stop the bot")
    print("\n📚 For detailed setup help, see: LOCAL_DEPLOYMENT_GUIDE.md")


if __name__ == "__main__":
    success = check_configuration()
    show_next_steps()

    if success:
        print("\n🚀 Ready to deploy!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix configuration issues first")
        sys.exit(1)
