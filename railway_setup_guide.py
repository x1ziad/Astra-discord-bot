#!/usr/bin/env python3
"""
Railway Environment Variables Setup Guide
Run this to see exactly what needs to be set in Railway dashboard
"""

def print_railway_setup_guide():
    print("🚀 RAILWAY ENVIRONMENT VARIABLES SETUP GUIDE")
    print("=" * 60)
    print()
    print("📍 Go to: https://railway.app/dashboard")
    print("📍 Find your project: 'fortunate-spontaneity' or similar")
    print("📍 Click on your service: 'harmonious-insight' or the deployed bot")
    print("📍 Go to 'Variables' tab")
    print("📍 Add these environment variables:")
    print()
    
    variables = {
        'DISCORD_TOKEN': '<YOUR_ACTUAL_DISCORD_BOT_TOKEN>',
        'AI_API_KEY': 'YOUR_OPENROUTER_API_KEY_HERE',
        'AI_BASE_URL': 'https://openrouter.ai/api/v1',
        'AI_MODEL': 'deepseek/deepseek-r1:nitro',
        'AI_PROVIDER': 'universal'
    }
    
    for key, value in variables.items():
        if key == 'DISCORD_TOKEN':
            print(f"🔑 {key} = {value}")
            print("   ↳ Replace with your actual Discord bot token from Discord Developer Portal")
        else:
            print(f"🤖 {key} = {value}")
    
    print()
    print("⚡ After setting all variables:")
    print("   1. Railway will automatically redeploy")
    print("   2. Wait for deployment to complete")
    print("   3. Check logs for successful startup")
    print("   4. Test /ai_status and /chat commands")
    print()
    print("🔍 If you need your Discord token:")
    print("   • Go to https://discord.com/developers/applications")
    print("   • Select your bot application")
    print("   • Go to 'Bot' section")
    print("   • Copy the token (click 'Reset Token' if needed)")

if __name__ == "__main__":
    print_railway_setup_guide()
