"""
Get Bot Client ID and Generate Invitation URL
Run this script to get your bot's information and create the proper invite link
"""

import os
import sys
import asyncio
import discord
from urllib.parse import urlencode

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
            print()
            
            # Generate the correct invitation URL
            client_id = str(bot.user.id)
            permissions = "1099511627775"  # Full permissions
            scope = "bot applications.commands"
            
            params = {
                "client_id": client_id,
                "permissions": permissions,
                "scope": scope
            }
            
            base_url = "https://discord.com/api/oauth2/authorize"
            invite_url = f"{base_url}?{urlencode(params)}"
            
            print("🔗 CORRECT INVITATION URL:")
            print(f"   {invite_url}")
            print()
            
            print("📋 SETUP CHECKLIST:")
            print("1. ✅ Copy the URL above")
            print("2. 🌐 Go to Discord Developer Portal:")
            print("   https://discord.com/developers/applications")
            print(f"3. 🎯 Select your application (Client ID: {client_id})")
            print("4. ⚙️ OAuth2 → General → DISABLE 'Require OAuth2 Code Grant'")
            print("5. 🤖 Bot → ENABLE 'Public Bot' + DISABLE 'Require OAuth2 Code Grant'")
            print("6. 💾 Save changes")
            print("7. 🔗 Use the invitation URL above")
            print()
            
            print("🎉 This should fix the 'Integration requires code grant' error!")
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
