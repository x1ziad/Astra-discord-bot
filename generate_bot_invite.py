#!/usr/bin/env python3
"""
Generate the correct invite URL for your Astra Discord Bot with image generation permissions
"""


def generate_astra_bot_invite():
    """Generate invite URL for Astra Bot with proper permissions"""

    # Your bot's Client ID (you'll need to replace this with your actual Client ID)
    # Get this from: https://discord.com/developers/applications → Your Application → General Information
    CLIENT_ID = "YOUR_BOT_CLIENT_ID_HERE"  # Replace with actual Client ID

    # Required permissions for image generation (sum of all permission bits)
    permissions = (
        1024  # View Channels
        + 2048  # Send Messages
        + 16384  # Embed Links (CRITICAL for image display)
        + 32768  # Attach Files (backup for images)
        + 65536  # Read Message History
        + 262144  # Use External Emojis
        + 64  # Add Reactions
        + 8192  # Manage Messages (cleanup)
        + 2147483648  # Use Application Commands (slash commands)
    )

    # Generate the invite URL
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions={permissions}&scope=bot%20applications.commands"

    print("=" * 60)
    print("🚀 ASTRA BOT INVITE URL GENERATOR")
    print("=" * 60)
    print()

    if CLIENT_ID == "YOUR_BOT_CLIENT_ID_HERE":
        print("⚠️  You need to set your bot's Client ID first!")
        print()
        print("📋 Steps to get your Client ID:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Click on your Astra Bot application")
        print("3. Go to 'General Information'")
        print("4. Copy the 'Application ID' (this is your Client ID)")
        print("5. Replace 'YOUR_BOT_CLIENT_ID_HERE' in this script")
        print()
        print("🔧 Then run this script again!")

    else:
        print("✅ Generated Invite URL for your Astra Bot:")
        print()
        print(invite_url)
        print()
        print("📋 This URL includes permissions for:")
        print("   ✓ View Channels")
        print("   ✓ Send Messages")
        print("   ✓ Embed Links (for image display)")
        print("   ✓ Attach Files (backup method)")
        print("   ✓ Read Message History")
        print("   ✓ Use External Emojis")
        print("   ✓ Add Reactions")
        print("   ✓ Manage Messages")
        print("   ✓ Use Application Commands (slash commands)")
        print()
        print("🎯 Usage:")
        print("1. Click the URL above")
        print("2. Select your Discord server")
        print("3. Confirm the permissions")
        print("4. Test with `/test_permissions` command")
        print("5. Try image generation with `astra generate test robot`")

    print()
    print("💡 Permission Calculation: " + str(permissions))


if __name__ == "__main__":
    generate_astra_bot_invite()
