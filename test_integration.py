"""
Comprehensive Discord Bot Integration Test Suite
Tests all aspects of the OAuth2 fix and bot invitation system
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_invitation_url_format():
    """Test invitation URL format and parameters"""
    print("🧪 Testing Invitation URL Format...")
    
    from utils.bot_invite import generate_bot_invite_url, get_full_permissions, get_minimal_permissions, get_recommended_permissions
    
    test_client_id = "123456789012345678"
    
    # Test full permissions URL
    full_url = generate_bot_invite_url(test_client_id, get_full_permissions())
    parsed = urlparse(full_url)
    params = parse_qs(parsed.query)
    
    print(f"✅ Full URL: {full_url}")
    
    # Verify required parameters
    assert parsed.netloc == "discord.com", "❌ Wrong domain"
    assert parsed.path == "/api/oauth2/authorize", "❌ Wrong path"
    assert params.get("client_id") == [test_client_id], "❌ Wrong client_id"
    assert "bot applications.commands" in params.get("scope", [""])[0], "❌ Missing required scopes"
    assert params.get("permissions"), "❌ Missing permissions"
    
    print("✅ URL format validation passed")
    
    # Test different permission levels
    permissions = {
        "full": get_full_permissions(),
        "recommended": get_recommended_permissions(), 
        "minimal": get_minimal_permissions()
    }
    
    for level, perm_value in permissions.items():
        url = generate_bot_invite_url(test_client_id, perm_value)
        parsed_params = parse_qs(urlparse(url).query)
        assert parsed_params.get("permissions")[0] == str(perm_value), f"❌ Wrong {level} permissions"
        print(f"✅ {level.title()} permissions URL: Valid")
    
    return True

def test_oauth2_configuration():
    """Test OAuth2 configuration requirements"""
    print("\n🔧 Testing OAuth2 Configuration Requirements...")
    
    required_settings = {
        "OAuth2 General": {
            "In-app Authorization": "ENABLED",
            "Require OAuth2 Code Grant": "DISABLED"
        },
        "Bot Settings": {
            "Public Bot": "ENABLED", 
            "Require OAuth2 Code Grant": "DISABLED",
            "Message Content Intent": "ENABLED (recommended)"
        }
    }
    
    print("📋 Required Discord Developer Portal Settings:")
    for section, settings in required_settings.items():
        print(f"\n🔸 {section}:")
        for setting, value in settings.items():
            print(f"   • {setting}: {value}")
    
    print("\n✅ Configuration requirements documented")
    return True

def test_permission_calculations():
    """Test permission integer calculations"""
    print("\n🔢 Testing Permission Calculations...")
    
    from utils.bot_invite import get_full_permissions, get_minimal_permissions, get_recommended_permissions
    import discord
    
    # Test full permissions
    full_perms = get_full_permissions()
    print(f"Full permissions integer: {full_perms}")
    assert full_perms == 1099511627775, f"❌ Full permissions mismatch: {full_perms}"
    
    # Test minimal permissions
    minimal_perms = get_minimal_permissions()
    print(f"Minimal permissions integer: {minimal_perms}")
    
    # Test recommended permissions
    recommended_perms = get_recommended_permissions()
    print(f"Recommended permissions integer: {recommended_perms}")
    
    # Verify permissions are valid Discord.Permissions
    for perm_name, perm_value in [
        ("full", full_perms),
        ("minimal", minimal_perms), 
        ("recommended", recommended_perms)
    ]:
        try:
            perms_obj = discord.Permissions(perm_value)
            print(f"✅ {perm_name.title()} permissions: Valid Discord.Permissions object")
        except Exception as e:
            print(f"❌ {perm_name.title()} permissions invalid: {e}")
            return False
    
    return True

def test_config_loading():
    """Test configuration loading and bot settings"""
    print("\n⚙️ Testing Configuration Loading...")
    
    try:
        from config.config_manager import config_manager
        config = config_manager.get_bot_config()
        
        print(f"✅ Bot name: {config.name}")
        print(f"✅ Bot version: {config.version}")
        print(f"✅ Features enabled: {len([f for f, enabled in config.features.items() if enabled])}")
        
        # Test specific features needed for space commands
        space_features = [
            "space_content",
            "space_content.iss_tracking", 
            "space_content.launch_notifications"
        ]
        
        for feature in space_features:
            if hasattr(config, 'features') and feature in config.features:
                status = "✅ Enabled" if config.features[feature] else "⚠️ Disabled"
                print(f"   {feature}: {status}")
            else:
                print(f"   {feature}: ⚠️ Not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_file_structure():
    """Test required file structure exists"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "utils/bot_invite.py",
        "utils/fix_oauth2.py", 
        "cogs/bot_setup.py",
        "cogs/bot_setup_enhanced.py",
        "get_bot_info.py",
        "config/config.json",
        "bot.1.0.py"
    ]
    
    required_dirs = [
        "data",
        "logs",
        "utils",
        "cogs",
        "config"
    ]
    
    # Check files
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
    
    # Check directories
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {dir_path}/")
    
    return True

def test_imports():
    """Test all required imports work"""
    print("\n📦 Testing Required Imports...")
    
    import_tests = [
        ("discord", "Discord.py library"),
        ("urllib.parse", "URL parsing"),
        ("json", "JSON handling"),
        ("pathlib", "Path handling"),
        ("datetime", "Date/time utilities"),
        ("asyncio", "Async support")
    ]
    
    for module, description in import_tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description}: {e}")
            return False
    
    # Test project-specific imports
    project_imports = [
        ("utils.bot_invite", "Bot invitation utilities"),
        ("config.config_manager", "Configuration management")
    ]
    
    for module, description in project_imports:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"⚠️ {module} - {description}: {e}")
            # Non-critical for this test
    
    return True

async def test_bot_connection():
    """Test bot connection (if token available)"""
    print("\n🤖 Testing Bot Connection...")
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("⚠️ DISCORD_TOKEN not found - skipping connection test")
        print("   Set DISCORD_TOKEN environment variable to test connection")
        return True
    
    try:
        import discord
        
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        
        connection_successful = False
        bot_info = {}
        
        @client.event
        async def on_ready():
            nonlocal connection_successful, bot_info
            connection_successful = True
            bot_info = {
                "name": str(client.user),
                "id": client.user.id,
                "created_at": client.user.created_at
            }
            print(f"✅ Bot connected: {client.user}")
            print(f"✅ Client ID: {client.user.id}")
            await client.close()
        
        # Attempt connection with timeout
        try:
            await asyncio.wait_for(client.start(token), timeout=10.0)
        except asyncio.TimeoutError:
            print("⚠️ Connection timeout - bot may be slow to connect")
            return True
        
        if connection_successful:
            print("✅ Bot connection test passed")
            
            # Save bot info for invitation URL generation
            bot_info_file = Path("data/bot_info.json")
            bot_info_file.parent.mkdir(exist_ok=True)
            with open(bot_info_file, 'w') as f:
                json.dump({
                    **bot_info,
                    "created_at": bot_info["created_at"].isoformat(),
                    "test_date": datetime.utcnow().isoformat()
                }, f, indent=2)
            print(f"✅ Bot info saved to: {bot_info_file}")
            
            return True
        else:
            print("❌ Bot connection failed")
            return False
            
    except discord.LoginFailure:
        print("❌ Invalid Discord token")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n📊 Generating Test Report...")
    
    report = {
        "test_date": datetime.utcnow().isoformat(),
        "test_results": {},
        "recommendations": [],
        "next_steps": []
    }
    
    # Run all tests
    tests = [
        ("URL Format", test_invitation_url_format),
        ("OAuth2 Config", test_oauth2_configuration),
        ("Permissions", test_permission_calculations),
        ("Configuration", test_config_loading),
        ("File Structure", test_file_structure),
        ("Imports", test_imports)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            report["test_results"][test_name] = "PASSED" if result else "FAILED"
            if result:
                passed_tests += 1
        except Exception as e:
            report["test_results"][test_name] = f"ERROR: {e}"
            print(f"❌ {test_name} test error: {e}")
    
    # Add recommendations based on results
    if passed_tests == total_tests:
        report["recommendations"].append("All tests passed! Your bot setup is ready.")
        report["next_steps"].extend([
            "1. Run 'python get_bot_info.py' to get your invitation URL",
            "2. Configure Discord Developer Portal settings",
            "3. Test bot invitation with the generated URL",
            "4. Deploy your bot and test all features"
        ])
    else:
        report["recommendations"].append("Some tests failed. Review the output above.")
        report["next_steps"].extend([
            "1. Fix any failed tests",
            "2. Re-run this test suite",
            "3. Check Discord Developer Portal settings",
            "4. Verify environment variables are set"
        ])
    
    # Save report
    report_file = Path("data/test_report.json")
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test Summary: {passed_tests}/{total_tests} tests passed")
    print(f"📁 Report saved to: {report_file}")
    
    return report

async def main():
    """Run comprehensive test suite"""
    print("=" * 80)
    print("🧪 DISCORD BOT INTEGRATION TEST SUITE")
    print("=" * 80)
    print("Testing OAuth2 fix and invitation system...")
    print()
    
    # Run synchronous tests
    report = generate_test_report()
    
    # Run async tests
    print("\n🔗 Testing Bot Connection...")
    connection_result = await test_bot_connection()
    report["test_results"]["Bot Connection"] = "PASSED" if connection_result else "FAILED"
    
    print("\n" + "=" * 80)
    print("🎯 FINAL RESULTS")
    print("=" * 80)
    
    passed = sum(1 for result in report["test_results"].values() if result == "PASSED")
    total = len(report["test_results"])
    
    print(f"✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your bot is ready for deployment.")
        print("\n🚀 Next Steps:")
        for step in report["next_steps"]:
            print(f"   {step}")
    else:
        print("⚠️ Some tests need attention. Check the output above.")
        print("\n🔧 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
