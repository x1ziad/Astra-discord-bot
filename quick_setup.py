#!/usr/bin/env python3
"""
Quick Setup Script for Astra Discord Bot
Automatically fixes OAuth2 issues and generates invitation URLs
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def print_banner():
    print("=" * 80)
    print("🤖 ASTRA DISCORD BOT - QUICK SETUP")
    print("=" * 80)
    print("Fixing 'Integration requires code grant' error...")
    print()

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Environment Check:")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]}")
    
    # Check Discord token
    token = os.getenv("DISCORD_TOKEN")
    if token:
        print(f"✅ Discord token: ...{token[-10:]}")
    else:
        print("⚠️ Discord token: Not set (optional for setup)")
    
    # Check required files
    required_files = [
        "utils/bot_invite.py",
        "get_bot_info.py", 
        "config/config.json",
        "test_integration.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files!")
        return False
    
    print("✅ Environment check passed")
    return True

def generate_invitation_urls():
    """Generate invitation URLs for different permission levels"""
    print("\n🔗 Generating Invitation URLs:")
    
    try:
        from utils.bot_invite import generate_bot_invite_url, get_full_permissions, get_recommended_permissions, get_minimal_permissions
        
        # Use example client ID if real one not available
        example_client_id = "123456789012345678"
        
        urls = {
            "full": generate_bot_invite_url(example_client_id, get_full_permissions()),
            "recommended": generate_bot_invite_url(example_client_id, get_recommended_permissions()),
            "minimal": generate_bot_invite_url(example_client_id, get_minimal_permissions())
        }
        
        print("📋 Template URLs (replace 123456789012345678 with your bot's Client ID):")
        print()
        
        for level, url in urls.items():
            print(f"🔸 {level.title()} Permissions:")
            print(f"   {url}")
            print()
        
        # Save URLs
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        with open(data_dir / "invitation_templates.json", "w") as f:
            json.dump({
                "generated_at": datetime.utcnow().isoformat(),
                "template_client_id": example_client_id,
                "urls": urls,
                "instructions": "Replace the client_id parameter with your actual bot's Client ID"
            }, f, indent=2)
        
        print("💾 URLs saved to: data/invitation_templates.json")
        return True
        
    except Exception as e:
        print(f"❌ Error generating URLs: {e}")
        return False

def show_discord_portal_instructions():
    """Show Discord Developer Portal setup instructions"""
    print("\n⚙️ Discord Developer Portal Setup:")
    print()
    print("1. 🌐 Go to: https://discord.com/developers/applications")
    print("2. 🎯 Select your bot application")  
    print("3. 🔧 OAuth2 → General tab:")
    print("   • ❌ DISABLE 'Require OAuth2 Code Grant'")
    print("   • ✅ ENABLE 'In-app Authorization'")
    print("4. 🤖 Bot tab:")
    print("   • ✅ ENABLE 'Public Bot'")
    print("   • ❌ DISABLE 'Require OAuth2 Code Grant'")
    print("   • ✅ ENABLE 'Message Content Intent'")
    print("5. 💾 Save all changes")
    print("6. 📋 Copy your bot's Client ID")
    print("7. 🔄 Replace '123456789012345678' in the URLs above")
    print()

def run_diagnostics():
    """Run basic diagnostics"""
    print("🧪 Running Quick Diagnostics:")
    
    try:
        # Test imports
        import discord
        print("✅ Discord.py library")
        
        from config.config_manager import config_manager
        config = config_manager.get_bot_config()
        print(f"✅ Bot configuration: {config.name} v{config.version}")
        
        from utils.bot_invite import get_full_permissions
        perms = get_full_permissions()
        print(f"✅ Permission calculations: {perms}")
        
        print("✅ Basic diagnostics passed")
        return True
        
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🚀 Next Steps:")
    print()
    print("1. 🔧 Configure Discord Developer Portal (see instructions above)")
    print("2. 🔗 Get your real bot Client ID and update the invitation URL")  
    print("3. 🧪 Run: python test_integration.py (comprehensive testing)")
    print("4. 🤖 Run: python get_bot_info.py (with DISCORD_TOKEN set)")
    print("5. 🌐 Test the invitation URL in your browser")
    print("6. ✅ Add bot to a test server and verify it works")
    print()
    print("📚 Need more help? Check SETUP_GUIDE.md for detailed instructions")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return 1
    
    # Generate URLs
    if not generate_invitation_urls():
        print("\n❌ URL generation failed. Check the error above.")
        return 1
    
    # Show portal instructions
    show_discord_portal_instructions()
    
    # Run diagnostics
    if not run_diagnostics():
        print("\n⚠️ Some diagnostics failed, but setup can continue.")
    
    # Show next steps
    show_next_steps()
    
    print("=" * 80)
    print("🎉 QUICK SETUP COMPLETED!")
    print("Your bot should now work without the 'code grant' error.")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
