#!/usr/bin/env python3
"""
Railway Configuration Test Script
Test if the Railway configuration is working properly

Usage: python test_railway_config.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_railway_config():
    """Test the Railway configuration system"""
    print("🔍 Testing Railway Configuration...")
    print("=" * 50)
    
    # Test environment variables
    print("📋 Environment Variables Check:")
    required_vars = ["DISCORD_TOKEN"]
    optional_vars = [
        "AI_API_KEY", "OPENROUTER_API_KEY", "GITHUB_TOKEN", 
        "AI_PROVIDER", "AI_MODEL", "FREEPIK_API_KEY"
    ]
    
    missing_required = []
    available_optional = []
    missing_optional = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = f"***{value[-4:]}" if len(value) > 4 else "***SET***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: NOT SET")
            missing_required.append(var)
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                masked = f"***{value[-4:]}" if len(value) > 4 else "***SET***"
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
            available_optional.append(var)
        else:
            print(f"   ⚠️ {var}: NOT SET (optional)")
            missing_optional.append(var)
    
    print("\n" + "=" * 50)
    
    # Test Railway config import
    print("🔧 Testing Railway Config Import...")
    try:
        from config.railway_config import get_railway_config, setup_railway_logging
        print("   ✅ Railway config modules imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import Railway config: {e}")
        return False
    
    # Test Railway config initialization
    print("\n🏗️ Testing Railway Config Initialization...")
    try:
        if missing_required:
            print(f"   ⚠️ Skipping initialization test due to missing required vars: {missing_required}")
            print("   💡 Set DISCORD_TOKEN to test initialization")
            return True
        
        config = get_railway_config()
        print("   ✅ Railway config initialized successfully")
        
        # Test config methods
        print("\n⚙️ Testing Config Methods...")
        discord_config = config.get_discord_config()
        print(f"   ✅ Discord config: Token present = {bool(discord_config.get('token'))}")
        
        ai_config = config.get_active_ai_config()
        print(f"   ✅ AI config: Provider = {config.get_ai_provider()}")
        print(f"   ✅ AI config: Model = {ai_config.get('model', 'Not set')}")
        
        # Test config file creation
        print("\n📄 Testing Config File Creation...")
        config_file = config.create_config_file()
        print(f"   ✅ Config file created: {config_file}")
        
        if config_file.exists():
            print(f"   ✅ Config file exists and is readable")
            print(f"   📏 Config file size: {config_file.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Railway config initialization failed: {e}")
        print(f"   📝 Error type: {type(e).__name__}")
        import traceback
        print(f"   📋 Full traceback:")
        traceback.print_exc()
        return False

def test_bot_import():
    """Test if the main bot can be imported"""
    print("\n🤖 Testing Bot Import...")
    try:
        # This tests if all dependencies are available
        import bot
        print("   ✅ Bot module imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Bot import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Astra Bot - Railway Configuration Test")
    print("=" * 60)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    success = True
    
    # Test Railway configuration
    if not test_railway_config():
        success = False
    
    # Test bot import (optional)
    test_bot_import()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All critical tests passed!")
        print("💡 Your Railway configuration should work correctly.")
        if missing_required := [var for var in ["DISCORD_TOKEN"] if not os.getenv(var)]:
            print(f"⚠️  Remember to set these vars in Railway: {missing_required}")
    else:
        print("❌ Some tests failed!")
        print("🔧 Please fix the issues above before deploying to Railway.")
    
    print("\n🔗 Next steps:")
    print("   1. Fix any failed tests above")
    print("   2. Set missing environment variables in Railway")
    print("   3. Deploy and check Railway logs")
    print("   4. Use `python bot.1.0.py` to test locally")

if __name__ == "__main__":
    main()
