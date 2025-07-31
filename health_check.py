#!/usr/bin/env python3
"""
Astra Discord Bot - Configuration Health Check
Verifies that all required configurations are properly set.
"""

import os
import sys
from typing import List, Tuple

def load_env_file() -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env_vars

def check_environment() -> List[Tuple[str, bool, str]]:
    """Check environment variables and return status."""
    # Load from .env file
    env_vars = load_env_file()
    
    checks = []
    
    # Required variables
    discord_token = env_vars.get("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN")
    openai_key = env_vars.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    # Check Discord token
    if not discord_token or discord_token == "your-discord-bot-token-here":
        checks.append(("Discord Token", False, "Not configured - get from https://discord.com/developers/applications"))
    elif len(discord_token) < 50:
        checks.append(("Discord Token", False, "Invalid format - check your token"))
    else:
        checks.append(("Discord Token", True, "Configured"))
    
    # Check OpenAI API key
    if not openai_key or openai_key == "sk-your-openai-api-key-here":
        checks.append(("OpenAI API Key", False, "Not configured - get from https://platform.openai.com/api-keys"))
    elif not openai_key.startswith("sk-"):
        checks.append(("OpenAI API Key", False, "Invalid format - should start with 'sk-'"))
    else:
        checks.append(("OpenAI API Key", True, "Configured"))
    
    # Optional variables
    nasa_key = env_vars.get("NASA_API_KEY") or os.getenv("NASA_API_KEY", "DEMO_KEY")
    checks.append(("NASA API Key", True, f"Using: {nasa_key}"))
    
    notion_token = env_vars.get("NOTION_TOKEN") or os.getenv("NOTION_TOKEN")
    if notion_token:
        checks.append(("Notion Token", True, "Configured (optional)"))
    else:
        checks.append(("Notion Token", True, "Not configured (optional)"))
    
    return checks

def check_files() -> List[Tuple[str, bool, str]]:
    """Check required files exist."""
    checks = []
    
    required_files = [
        "bot.1.0.py",
        "ai_config.json",
        "requirements.txt",
        "cogs/ai_commands.py",
        "ai_chat.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            checks.append((f"File: {file_path}", True, "Exists"))
        else:
            checks.append((f"File: {file_path}", False, "Missing"))
    
    return checks

def main():
    """Run all health checks."""
    print("🏥 Astra Discord Bot - Health Check")
    print("=" * 40)
    
    all_good = True
    
    # Environment checks
    print("\n📋 Environment Variables:")
    env_checks = check_environment()
    for name, status, message in env_checks:
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}: {message}")
        if not status and name in ["Discord Token", "OpenAI API Key"]:
            all_good = False
    
    # File checks
    print("\n📁 Required Files:")
    file_checks = check_files()
    for name, status, message in file_checks:
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}: {message}")
        if not status:
            all_good = False
    
    # Docker checks
    print("\n🐳 Docker Configuration:")
    docker_files = ["Dockerfile", "docker-compose.yml", ".env.example"]
    for file_path in docker_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}: Exists")
        else:
            print(f"  ❌ {file_path}: Missing")
    
    # Summary
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All critical checks passed! Your bot should work correctly.")
        print("\n🚀 To start the bot:")
        print("   Docker: ./setup.sh or docker-compose up -d")
        print("   Manual: python bot.1.0.py")
    else:
        print("⚠️  Some critical issues found. Please fix them before running the bot.")
        print("\n📖 See README.md for setup instructions.")
        sys.exit(1)

if __name__ == "__main__":
    main()