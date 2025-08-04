"""
Discord Developer Portal Setup Checker
Helps diagnose and fix "Integration requires code grant" errors
"""

import os
import sys
from pathlib import Path

def check_discord_setup():
    """Check Discord bot configuration and provide setup guidance"""
    
    print("=" * 80)
    print("🔍 DISCORD BOT SETUP DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Check environment variables
    print("📋 ENVIRONMENT VARIABLES:")
    token = os.getenv("DISCORD_TOKEN")
    if token:
        print(f"✅ DISCORD_TOKEN: Set (ends with ...{token[-10:]})")
    else:
        print("❌ DISCORD_TOKEN: Not found!")
        print("   Please set your Discord bot token as an environment variable.")
    print()
    
    # Get bot info from config if available
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from config.config_manager import config_manager
        config = config_manager.get_bot_config()
        print(f"✅ Bot Name: {config.name}")
        print(f"✅ Bot Version: {config.version}")
        if hasattr(config, 'client_id'):
            client_id = config.client_id
        else:
            client_id = "YOUR_CLIENT_ID"
    except Exception as e:
        print(f"⚠️ Could not load bot config: {e}")
        client_id = "YOUR_CLIENT_ID"
    
    print()
    print("🔧 DISCORD DEVELOPER PORTAL SETUP:")
    print()
    print("The 'Integration requires code grant' error means your Discord")
    print("application needs proper OAuth2 configuration. Follow these steps:")
    print()
    
    print("1. 📱 Go to Discord Developer Portal:")
    print("   https://discord.com/developers/applications")
    print()
    
    print(f"2. 🎯 Select Your Application:")
    print(f"   Look for your bot application (Client ID: {client_id})")
    print()
    
    print("3. ⚙️ Fix OAuth2 Settings:")
    print("   • Go to 'OAuth2' → 'General' section")
    print("   • Find 'Authorization Method'")
    print("   • Make sure 'In-app Authorization' is ENABLED")
    print("   • Make sure 'Require OAuth2 Code Grant' is DISABLED")
    print("   • Click 'Save Changes'")
    print()
    
    print("4. 🤖 Bot Section Settings:")
    print("   • Go to 'Bot' section")
    print("   • Make sure 'Public Bot' is ENABLED")
    print("   • Make sure 'Require OAuth2 Code Grant' is DISABLED")
    print("   • Click 'Save Changes'")
    print()
    
    print("5. 🔗 Generate New Invitation URL:")
    # Generate the correct invitation URL
    from utils.bot_invite import generate_bot_invite_url, get_full_permissions
    
    if client_id != "YOUR_CLIENT_ID":
        invite_url = generate_bot_invite_url(client_id, get_full_permissions())
        print(f"   {invite_url}")
    else:
        print("   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=1099511627775&scope=bot%20applications.commands")
        print("   (Replace YOUR_CLIENT_ID with your actual Client ID)")
    print()
    
    print("6. ✅ Test the New URL:")
    print("   • Copy the URL above")
    print("   • Paste it in your browser")
    print("   • Select a server you manage")
    print("   • You should NOT see the 'code grant' error anymore")
    print()
    
    print("🎯 KEY POINTS TO REMEMBER:")
    print()
    print("✅ DO:")
    print("   • Enable 'Public Bot'")
    print("   • Enable 'In-app Authorization'") 
    print("   • Use scope: 'bot applications.commands'")
    print("   • Use proper permissions integer")
    print()
    print("❌ DON'T:")
    print("   • Enable 'Require OAuth2 Code Grant'")
    print("   • Use only 'applications.commands' scope (missing 'bot')")
    print("   • Forget to save changes in Developer Portal")
    print()
    
    print("🆘 STILL HAVING ISSUES?")
    print()
    print("1. Double-check all settings in Developer Portal")
    print("2. Wait 5-10 minutes for changes to propagate")
    print("3. Try in incognito/private browser window")
    print("4. Make sure you have 'Manage Server' permission")
    print("5. Check Discord's status page for API issues")
    print()
    
    print("=" * 80)
    
    return client_id

def generate_fixed_invite_url(client_id: str) -> str:
    """Generate the corrected invitation URL"""
    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": client_id,
        "permissions": "1099511627775",  # Full permissions
        "scope": "bot applications.commands"  # CRITICAL: Both scopes needed
    }
    
    from urllib.parse import urlencode
    return f"{base_url}?{urlencode(params)}"

if __name__ == "__main__":
    client_id = check_discord_setup()
    
    print("\n" + "=" * 80)
    print("💡 QUICK FIX SUMMARY:")
    print("=" * 80)
    print()
    print("1. Go to: https://discord.com/developers/applications")
    print("2. Select your bot application")
    print("3. OAuth2 → General → DISABLE 'Require OAuth2 Code Grant'")
    print("4. Bot → ENABLE 'Public Bot' + DISABLE 'Require OAuth2 Code Grant'")
    print("5. Save changes and use the new invitation URL")
    print()
    print("The error happens when Discord thinks your bot needs a 'code grant'")
    print("flow instead of the simpler bot invitation process.")
    print()
    print("=" * 80)
