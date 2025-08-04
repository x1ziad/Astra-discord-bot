"""
Enhanced Bot Information & Invitation URL Generator
Run this script to get your bot's information and create the proper invite link
"""

import os
import sys
import asyncio
import discord
from urllib.parse import urlencode
import json
from pathlib import Path


async def get_bot_info():
    """Get bot information and generate invitation URL"""

    print("=" * 80)
    print("🤖 BOT INFORMATION & INVITATION URL GENERATOR")
    print("=" * 80)
    print()

    # Check for Discord token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN environment variable not found!")
        print()
        print("Please set your Discord bot token:")
        print("export DISCORD_TOKEN='your_bot_token_here'")
        print()
        return

    try:
        # Create a minimal bot instance to get client ID
        intents = discord.Intents.default()
        bot = discord.Client(intents=intents)

        @bot.event
        async def on_ready():
            print(f"✅ Bot connected: {bot.user}")
            print(f"🆔 Client ID: {bot.user.id}")
            print(f"🏷️ Bot Tag: {bot.user}")
            print(f"📅 Account Created: {bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Check if bot is verified
            if hasattr(bot.user, 'public_flags'):
                flags = bot.user.public_flags
                if flags.verified_bot:
                    print("✅ Verified Bot: True")
                elif flags.verified_bot_developer:
                    print("✅ Verified Bot Developer: True")
                else:
                    print("ℹ️ Verification Status: Not verified (normal for new bots)")
            print()

            # Generate multiple invitation URLs with different permission levels
            client_id = str(bot.user.id)

            # Full permissions
            full_permissions = "1099511627775"
            recommended_permissions = "1099511627775"  # Same as full for this bot
            minimal_permissions = "2147551424"  # Basic permissions

            base_url = "https://discord.com/api/oauth2/authorize"
            scope = "bot applications.commands"

            # Generate URLs
            full_url = f"{base_url}?{urlencode({'client_id': client_id, 'permissions': full_permissions, 'scope': scope})}"
            recommended_url = f"{base_url}?{urlencode({'client_id': client_id, 'permissions': recommended_permissions, 'scope': scope})}"
            minimal_url = f"{base_url}?{urlencode({'client_id': client_id, 'permissions': minimal_permissions, 'scope': scope})}"

            print("🔗 INVITATION URLS:")
            print()
            print("🌟 RECOMMENDED (Full Features):")
            print(f"   {full_url}")
            print()
            print("⚡ MINIMAL (Basic Functions):")
            print(f"   {minimal_url}")
            print()

            # Save URLs to file for easy access
            urls_data = {
                "bot_info": {
                    "name": str(bot.user),
                    "id": bot.user.id,
                    "created_at": bot.user.created_at.isoformat()
                },
                "invitation_urls": {
                    "full_permissions": full_url,
                    "recommended": recommended_url,
                    "minimal": minimal_url
                },
                "permissions": {
                    "full": full_permissions,
                    "minimal": minimal_permissions
                }
            }

            # Save to data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            with open(data_dir / "bot_invitation_urls.json", "w") as f:
                json.dump(urls_data, f, indent=2)
            
            print("💾 Invitation URLs saved to: data/bot_invitation_urls.json")
            print()

            print("📋 DISCORD DEVELOPER PORTAL SETUP:")
            print("1. 🌐 Go to: https://discord.com/developers/applications")
            print(f"2. 🎯 Select your application (Client ID: {client_id})")
            print("3. ⚙️ OAuth2 → General:")
            print("   • ❌ DISABLE 'Require OAuth2 Code Grant'")
            print("   • ✅ ENABLE 'In-app Authorization'")
            print("4. 🤖 Bot Section:")
            print("   • ✅ ENABLE 'Public Bot'")
            print("   • ❌ DISABLE 'Require OAuth2 Code Grant'")
            print("   • ✅ ENABLE 'Message Content Intent' (if needed)")
            print("5. 💾 Save all changes")
            print("6. 🔗 Use the invitation URL above")
            print()

            print("🧪 TESTING CHECKLIST:")
            print("✅ Copy the RECOMMENDED URL above")
            print("✅ Open in browser (try incognito mode if issues)")
            print("✅ Select a test server you manage")
            print("✅ You should NOT see 'code grant' error")
            print("✅ Complete the authorization")
            print("✅ Bot should appear in server member list")
            print("✅ Test with /ping command")
            print()

            print("🎉 SUCCESS! Your bot should now integrate properly!")
            print()

            await bot.close()

        # Connect to Discord briefly to get bot info
        await bot.start(token)

    except discord.LoginFailure:
        print("❌ Invalid Discord token!")
        print("Please check your DISCORD_TOKEN environment variable.")
    except Exception as e:
        print(f"❌ Error connecting to Discord: {e}")


if __name__ == "__main__":
    asyncio.run(get_bot_info())
