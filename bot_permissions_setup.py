#!/usr/bin/env python3
"""
Discord Bot Permission Setup Guide
This script helps you ensure your Discord bot has the correct permissions for image generation
"""

import json
from typing import Dict, List


def generate_bot_invite_url(client_id: str, permissions: int = None) -> str:
    """Generate a Discord bot invite URL with proper permissions"""

    # Required permissions for image generation (bitfield)
    REQUIRED_PERMISSIONS = {
        "view_channels": 1024,  # View Channels
        "send_messages": 2048,  # Send Messages
        "embed_links": 16384,  # Embed Links
        "attach_files": 32768,  # Attach Files
        "read_message_history": 65536,  # Read Message History
        "use_external_emojis": 262144,  # Use External Emojis
        "add_reactions": 64,  # Add Reactions
        "use_slash_commands": 2147483648,  # Use Application Commands
    }

    # Calculate total permissions needed
    if permissions is None:
        permissions = sum(REQUIRED_PERMISSIONS.values())

    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot%20applications.commands"

    return invite_url


def check_permission_requirements() -> Dict[str, List[str]]:
    """Return permission requirements for different bot features"""

    return {
        "Essential (Required)": [
            "View Channels - Bot needs to see channels",
            "Send Messages - Basic communication",
            "Use Slash Commands - Modern Discord commands",
            "Read Message History - Context understanding",
        ],
        "Image Generation (Critical)": [
            "Embed Links - Display image embeds",
            "Attach Files - Send image files if needed",
            "Use External Emojis - Status indicators and reactions",
        ],
        "Enhanced Features (Recommended)": [
            "Add Reactions - Interactive feedback",
            "Manage Messages - Clean up status messages",
            "Mention Everyone - Important announcements (admin only)",
        ],
        "Administrative (Optional)": [
            "Kick Members - Moderation features",
            "Ban Members - Advanced moderation",
            "Manage Roles - Role management commands",
            "View Audit Log - Security monitoring",
        ],
    }


def print_permission_guide():
    """Print a comprehensive permission setup guide"""

    print("=" * 60)
    print("🤖 DISCORD BOT PERMISSION SETUP GUIDE")
    print("=" * 60)
    print()

    requirements = check_permission_requirements()

    for category, perms in requirements.items():
        print(f"📋 {category}:")
        for perm in perms:
            print(f"   ✓ {perm}")
        print()

    print("🔧 SETUP METHODS:")
    print("-" * 30)
    print()

    print("Method 1: Re-invite Bot with Correct Permissions")
    print("   1. Get your bot's Client ID from Discord Developer Portal")
    print("   2. Use the generate_bot_invite_url() function above")
    print("   3. Visit the generated URL and re-authorize the bot")
    print()

    print("Method 2: Manual Permission Setup")
    print("   1. Go to your Discord Server")
    print("   2. Server Settings → Roles")
    print("   3. Find your bot's role")
    print("   4. Enable the permissions listed above")
    print()

    print("Method 3: Channel-Specific Permissions")
    print("   1. Go to the channel where bot will operate")
    print("   2. Channel Settings → Permissions")
    print("   3. Add your bot and enable required permissions")
    print()

    print("🧪 TESTING:")
    print("-" * 30)
    print("   • Use `/permissions` command in Discord to check")
    print("   • Try `astra generate test robot` to verify image generation")
    print("   • Check bot logs for permission errors")
    print()

    print("⚠️  TROUBLESHOOTING:")
    print("-" * 30)
    print("   • Bot not responding: Check 'Send Messages' permission")
    print("   • Images not showing: Check 'Embed Links' permission")
    print("   • File upload fails: Check 'Attach Files' permission")
    print("   • Reactions missing: Check 'Use External Emojis' permission")
    print()


def generate_permission_checker_json() -> str:
    """Generate a JSON configuration for permission checking"""

    config = {
        "bot_permissions": {
            "essential": [
                "view_channels",
                "send_messages",
                "use_slash_commands",
                "read_message_history",
            ],
            "image_generation": ["embed_links", "attach_files", "use_external_emojis"],
            "enhanced": ["add_reactions", "manage_messages"],
        },
        "permission_values": {
            "view_channels": 1024,
            "send_messages": 2048,
            "embed_links": 16384,
            "attach_files": 32768,
            "read_message_history": 65536,
            "use_external_emojis": 262144,
            "add_reactions": 64,
            "use_slash_commands": 2147483648,
            "manage_messages": 8192,
        },
        "troubleshooting": {
            "bot_not_responding": "Check 'Send Messages' and 'View Channels' permissions",
            "images_not_showing": "Check 'Embed Links' permission",
            "file_upload_fails": "Check 'Attach Files' permission",
            "slash_commands_missing": "Check 'Use Application Commands' permission",
        },
    }

    return json.dumps(config, indent=2)


if __name__ == "__main__":
    print_permission_guide()

    # Example usage
    print("💡 EXAMPLE BOT INVITE URL:")
    print("-" * 30)
    print("Replace YOUR_BOT_CLIENT_ID with your actual bot's Client ID:")
    print()
    example_url = generate_bot_invite_url("YOUR_BOT_CLIENT_ID")
    print(example_url)
    print()

    print("📄 PERMISSION CONFIG (save as permissions.json):")
    print("-" * 30)
    print(generate_permission_checker_json())
