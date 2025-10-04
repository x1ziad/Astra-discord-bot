#!/usr/bin/env python3
"""
🔒 SECURE API KEY MANAGER
Safely manages API keys and ensures they're never exposed publicly
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def secure_env_file():
    """Secure the .env file by backing up real keys and using placeholders"""

    env_file = Path(".env")
    backup_dir = Path("secure_backup")

    if not env_file.exists():
        print("❌ .env file not found")
        return

    # Create secure backup directory (this should be kept private)
    backup_dir.mkdir(exist_ok=True)

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f".env.backup.{timestamp}"

    # Copy real .env to secure backup
    shutil.copy2(env_file, backup_file)
    print(f"✅ Real API keys backed up to: {backup_file}")
    print("🔒 Keep this backup file SECURE and PRIVATE!")

    # Replace .env with template
    template_file = Path(".env.template")
    if template_file.exists():
        shutil.copy2(template_file, env_file)
        print("✅ .env file secured with placeholders")
    else:
        # Create secure placeholder .env
        secure_content = """# 🔒 SECURE CONFIGURATION - NO REAL KEYS EXPOSED
# Replace these placeholders with your actual API keys

DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CLIENT_ID=your_discord_client_id_here

OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
AI_API_KEY=your_openrouter_api_key_here

AI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=x-ai/grok-code-fast-1
AI_PROVIDER=universal
AI_MAX_TOKENS=1000

NASA_API_KEY=your_nasa_api_key_here
NOTION_TOKEN=your_notion_token_here
MAGICHOUR_API_KEY=your_magichour_api_key_here

SPACE_CHANNEL_ID=your_space_channel_id_here

ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
"""
        env_file.write_text(secure_content)
        print("✅ .env file secured with placeholders")

    # Update .gitignore to ensure security
    gitignore = Path(".gitignore")
    secure_patterns = [
        ".env",
        ".env.*",
        "*.env",
        "secure_backup/",
        "**/.env",
        "**/secure_backup/",
    ]

    if gitignore.exists():
        content = gitignore.read_text()
        new_patterns = []
        for pattern in secure_patterns:
            if pattern not in content:
                new_patterns.append(pattern)

        if new_patterns:
            content += "\n# Secure environment files\n" + "\n".join(new_patterns) + "\n"
            gitignore.write_text(content)
            print(f"✅ Added {len(new_patterns)} security patterns to .gitignore")

    print("\n🔒 SECURITY STATUS:")
    print("✅ Real API keys safely backed up")
    print("✅ Public .env file secured with placeholders")
    print("✅ .gitignore updated for security")
    print("\n⚠️  IMPORTANT:")
    print("- Your real API keys are in secure_backup/ folder")
    print("- Keep secure_backup/ folder PRIVATE and LOCAL only")
    print("- For deployment, use your hosting platform's secure environment variables")
    print("- Never commit secure_backup/ to git")


def restore_env_file(backup_timestamp=None):
    """Restore .env from backup (for local development)"""

    backup_dir = Path("secure_backup")
    if not backup_dir.exists():
        print("❌ No secure backup directory found")
        return

    backups = list(backup_dir.glob(".env.backup.*"))
    if not backups:
        print("❌ No backup files found")
        return

    if backup_timestamp:
        backup_file = backup_dir / f".env.backup.{backup_timestamp}"
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_file}")
            return
    else:
        # Use most recent backup
        backup_file = max(backups, key=lambda p: p.stat().st_mtime)

    shutil.copy2(backup_file, ".env")
    print(f"✅ Restored .env from: {backup_file}")
    print("⚠️  Remember: This contains real API keys - keep secure!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        timestamp = sys.argv[2] if len(sys.argv) > 2 else None
        restore_env_file(timestamp)
    else:
        secure_env_file()
