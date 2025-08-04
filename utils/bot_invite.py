"""
Discord Bot Invitation URL Generator
Generates proper invitation URLs with correct scopes and permissions
"""

import discord
from urllib.parse import urlencode


def generate_bot_invite_url(
    client_id: str,
    permissions: int = 1099511627775,
    guild_id: str = None,
    disable_guild_select: bool = False,
) -> str:
    """
    Generate a proper Discord bot invitation URL

    Args:
        client_id: Your Discord application's Client ID
        permissions: Permission integer (default: full permissions)
        guild_id: Specific guild ID to install to (optional)
        disable_guild_select: Whether to disable guild selection

    Returns:
        Complete invitation URL
    """

    base_url = "https://discord.com/api/oauth2/authorize"

    params = {
        "client_id": client_id,
        "permissions": str(permissions),
        "scope": "bot applications.commands",  # This is the key fix!
    }

    if guild_id:
        params["guild_id"] = guild_id

    if disable_guild_select:
        params["disable_guild_select"] = "true"

    return f"{base_url}?{urlencode(params)}"


def get_permission_calculator_url() -> str:
    """Get Discord's permission calculator URL"""
    return "https://discordapi.com/permissions.html"


def get_full_permissions() -> int:
    """Get the integer for full bot permissions"""
    return 1099511627775


def get_minimal_permissions() -> int:
    """Get minimal permissions for basic bot functionality"""
    permissions = discord.Permissions()
    permissions.read_messages = True
    permissions.send_messages = True
    permissions.embed_links = True
    permissions.attach_files = True
    permissions.read_message_history = True
    permissions.use_external_emojis = True
    permissions.add_reactions = True
    return permissions.value


def get_recommended_permissions() -> int:
    """Get recommended permissions for Astra bot"""
    permissions = discord.Permissions()
    
    # Essential permissions
    permissions.read_messages = True
    permissions.send_messages = True
    permissions.embed_links = True
    permissions.attach_files = True
    permissions.read_message_history = True
    permissions.use_external_emojis = True
    permissions.add_reactions = True
    
    # Thread permissions (Discord.py 2.0+)
    permissions.create_public_threads = True
    permissions.create_private_threads = True
    permissions.send_messages_in_threads = True
    
    # Moderation permissions
    permissions.manage_messages = True
    permissions.manage_channels = True
    permissions.kick_members = True
    permissions.ban_members = True
    permissions.manage_roles = True
    
    # Advanced permissions
    permissions.mention_everyone = True
    permissions.manage_webhooks = True
    permissions.view_audit_log = True
    
    return permissions.value
def print_invitation_info(client_id: str):
    """Print invitation URLs and setup information"""
    print("=" * 80)
    print("🤖 DISCORD BOT INVITATION SETUP")
    print("=" * 80)
    print()

    print("🔗 INVITATION URLS:")
    print()

    # Full permissions URL
    full_url = generate_bot_invite_url(client_id, get_full_permissions())
    print(f"📋 Full Permissions (Recommended):")
    print(f"   {full_url}")
    print()

    # Minimal permissions URL
    minimal_url = generate_bot_invite_url(client_id, get_minimal_permissions())
    print(f"📋 Minimal Permissions:")
    print(f"   {minimal_url}")
    print()

    # Recommended permissions URL
    recommended_url = generate_bot_invite_url(client_id, get_recommended_permissions())
    print(f"📋 Recommended Permissions:")
    print(f"   {recommended_url}")
    print()

    print("⚙️ SETUP INSTRUCTIONS:")
    print()
    print("1. Copy one of the URLs above")
    print("2. Paste it in your browser")
    print("3. Select the server you want to add the bot to")
    print("4. Review and confirm the permissions")
    print("5. Click 'Authorize'")
    print()

    print("🔧 IMPORTANT NOTES:")
    print()
    print("• Make sure you're logged into Discord in your browser")
    print("• You need 'Manage Server' permission on the target server")
    print("• The bot will appear in your server's member list once added")
    print("• Use /ping to test if the bot is working correctly")
    print()

    print("📱 DEVELOPER PORTAL SETTINGS:")
    print()
    print("If you're still having issues, check these settings:")
    print("1. Go to https://discord.com/developers/applications")
    print(f"2. Select your application (Client ID: {client_id})")
    print("3. Go to 'Bot' section")
    print("4. Make sure 'Public Bot' is enabled")
    print("5. Ensure 'Require OAuth2 Code Grant' is DISABLED")
    print("6. Save changes and try the invitation URL again")
    print()

    print("=" * 80)


if __name__ == "__main__":
    # Example usage - replace with your actual client ID
    example_client_id = "YOUR_BOT_CLIENT_ID_HERE"

    print("To use this script:")
    print("1. Replace 'YOUR_BOT_CLIENT_ID_HERE' with your actual bot's Client ID")
    print("2. Run: python utils/bot_invite.py")
    print()
    print("Or use it in your code:")
    print(f"from utils.bot_invite import generate_bot_invite_url")
    print(f"url = generate_bot_invite_url('your_client_id')")
