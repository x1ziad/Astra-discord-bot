#!/usr/bin/env python3
"""
Test script for Space Cog features in Astra Bot
This will test all space-related functionality without requiring Discord
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_space_features():
    """Test all space cog features"""
    print("🚀 Testing Astra Bot Space Features")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n📋 1. Checking Environment Variables:")
    env_vars = {
        "DISCORD_TOKEN": "Discord Bot Token (Required)",
        "NASA_API_KEY": "NASA API Key (Optional - uses DEMO_KEY if not set)",
        "OPENAI_API_KEY": "OpenAI API Key (Optional for AI features)",
        "ANTHROPIC_API_KEY": "Anthropic API Key (Optional for AI features)",
        "NOTION_TOKEN": "Notion API Token (Optional for Notion integration)",
        "NOTION_DATABASE_ID": "Notion Database ID (Optional for Notion integration)"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Not Set"
        if var == "NASA_API_KEY" and not value:
            status = "⚠️ Using DEMO_KEY (limited usage)"
        elif var == "DISCORD_TOKEN" and not value:
            status = "🚫 REQUIRED - Bot won't start"
        elif not value:
            status = "⭕ Optional"
        
        print(f"  {var}: {status} - {description}")
    
    # Test 2: Check data directories
    print("\n📁 2. Checking Data Directories:")
    data_dirs = [
        "data",
        "data/space",
        "data/conversations",
        "data/analytics"
    ]
    
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}: Exists")
        else:
            print(f"  📁 {dir_path}: Creating...")
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path}: Created")
    
    # Test 3: Test Space Cog initialization
    print("\n🤖 3. Testing Space Cog Components:")
    
    try:
        # Import space cog
        from cogs.space import Space
        print("  ✅ Space cog import: Success")
        
        # Mock bot for testing
        class MockBot:
            def __init__(self):
                import logging
                self.logger = logging.getLogger("test")
                self.logger.setLevel(logging.INFO)
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        
        # Initialize space cog
        mock_bot = MockBot()
        space_cog = Space(mock_bot)
        print("  ✅ Space cog initialization: Success")
        print(f"  📊 Space facts loaded: {len(space_cog.space_facts)} facts")
        
    except Exception as e:
        print(f"  ❌ Space cog initialization: Failed - {e}")
        return
    
    # Test 4: Test space facts
    print("\n📚 4. Testing Space Facts:")
    try:
        if space_cog.space_facts:
            print(f"  ✅ Facts available: {len(space_cog.space_facts)} facts")
            print(f"  📝 Sample fact: {space_cog.space_facts[0][:100]}...")
        else:
            print("  ❌ No space facts found")
    except Exception as e:
        print(f"  ❌ Space facts test failed: {e}")
    
    # Test 5: Test NASA API connectivity (if API key available)
    print("\n🛰️ 5. Testing NASA API:")
    nasa_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test APOD endpoint
            url = "https://api.nasa.gov/planetary/apod"
            params = {"api_key": nasa_key}
            
            print(f"  🔍 Testing with API key: {'Custom' if nasa_key != 'DEMO_KEY' else 'DEMO_KEY'}")
            
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print("  ✅ NASA APOD API: Success")
                    print(f"  📅 Today's APOD: {data.get('title', 'Unknown')}")
                elif response.status == 429:
                    print("  ⚠️ NASA APOD API: Rate limited (expected with DEMO_KEY)")
                else:
                    print(f"  ❌ NASA APOD API: Error {response.status}")
                    
    except Exception as e:
        print(f"  ❌ NASA API test failed: {e}")
    
    # Test 6: Test ISS API
    print("\n🛰️ 6. Testing ISS Tracking API:")
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test ISS location
            async with session.get("http://api.open-notify.org/iss-now.json", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    lat = data["iss_position"]["latitude"]
                    lon = data["iss_position"]["longitude"]
                    print("  ✅ ISS Location API: Success")
                    print(f"  📍 Current ISS position: {lat}°, {lon}°")
                else:
                    print(f"  ❌ ISS Location API: Error {response.status}")
            
            # Test astronauts in space
            async with session.get("http://api.open-notify.org/astros.json", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    total_people = data.get("number", 0)
                    iss_crew = [person for person in data.get("people", []) if person.get("craft") == "ISS"]
                    print(f"  ✅ Astronauts API: Success")
                    print(f"  👨‍🚀 People in space: {total_people}, ISS crew: {len(iss_crew)}")
                else:
                    print(f"  ❌ Astronauts API: Error {response.status}")
                    
    except Exception as e:
        print(f"  ❌ ISS API tests failed: {e}")
    
    # Test 7: Test configuration
    print("\n⚙️ 7. Testing Configuration:")
    try:
        from config.enhanced_config import config_manager
        print("  ✅ Enhanced config import: Success")
        
        # Test color configuration
        try:
            space_color = config_manager.get_color("space")
            print(f"  🎨 Space theme color: {space_color}")
        except:
            print("  ⚠️ Space color not configured, using default")
        
        # Test feature flags
        try:
            space_enabled = config_manager.get_feature_setting("space_content", True)
            print(f"  🔧 Space content feature: {'Enabled' if space_enabled else 'Disabled'}")
        except:
            print("  ⚠️ Feature flags not configured, using defaults")
            
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
    
    # Test 8: Check required Python packages
    print("\n📦 8. Checking Required Packages:")
    required_packages = [
        ("discord.py", "discord"),
        ("aiohttp", "aiohttp"),  
        ("python-dotenv", "dotenv"),
        ("sqlite3", "sqlite3")
    ]
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}: Available")
        except ImportError:
            print(f"  ❌ {package_name}: Missing - install with: pip install {package_name}")
    
    # Test 9: Test bot startup readiness
    print("\n🎯 9. Bot Startup Readiness:")
    
    discord_token = os.getenv("DISCORD_TOKEN")
    if discord_token and discord_token != "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("  ✅ Discord token: Configured")
        print("  ✅ Bot startup: Ready to launch with 'python bot.1.0.py'")
    else:
        print("  🚫 Discord token: Not configured")
        print("  ❌ Bot startup: Cannot start without DISCORD_TOKEN")
        print("  💡 Set your Discord token: export DISCORD_TOKEN='your_token_here'")
    
    print("\n" + "=" * 50)
    print("🎉 Space Features Test Complete!")
    print("\n💡 To run the bot:")
    print("1. Set DISCORD_TOKEN environment variable")
    print("2. Optional: Set NASA_API_KEY for better API limits")
    print("3. Run: python bot.1.0.py")
    print("\n🚀 Available Space Commands:")
    print("• /space apod - NASA Astronomy Picture of the Day")
    print("• /space fact - Random space fact")
    print("• /space iss - Track the International Space Station")
    print("• /space meteor - Meteor shower information")
    print("• /space launch - Upcoming space launches")
    print("• /space planets [name] - Solar system planet information")

if __name__ == "__main__":
    asyncio.run(test_space_features())
