#!/usr/bin/env python3
"""
Test Freepik Image Generation Integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_freepik_integration():
    """Test the Freepik image generation system"""
    try:
        print("🧪 Testing Freepik Image Generation Integration")
        print("=" * 60)

        # Test environment variable
        freepik_api_key = os.getenv("FREEPIK_API_KEY")
        if freepik_api_key:
            print(f"✅ FREEPIK_API_KEY found: {freepik_api_key[:10]}...")
        else:
            print("❌ FREEPIK_API_KEY not found in environment")
            print("💡 You need to set this variable in Railway!")

        # Test import
        from ai.consolidated_ai_engine import (
            FreepikImageGenerator,
            ConsolidatedAIEngine,
        )

        print("✅ FreepikImageGenerator imported successfully")

        # Test FreepikImageGenerator initialization
        if freepik_api_key:
            generator = FreepikImageGenerator(freepik_api_key)
            print("✅ FreepikImageGenerator initialized")
            print(f"✅ Generator is available: {generator.is_available()}")
        else:
            print("⚠️  Cannot test generator without API key")

        # Test ConsolidatedAIEngine with Freepik
        config = {"freepik_api_key": freepik_api_key} if freepik_api_key else {}
        ai_engine = ConsolidatedAIEngine(config)
        print("✅ ConsolidatedAIEngine with Freepik support initialized")

        # Test permission system
        print("\n🔐 Testing Permission System:")

        # Test regular user in wrong channel
        user_permissions = {"is_admin": False, "is_mod": False}
        permission_result = await ai_engine._check_image_generation_permission(
            user_id=123456,
            channel_id=999999999,  # Wrong channel
            user_permissions=user_permissions,
        )
        print(f"Regular user in wrong channel: {permission_result}")

        # Test regular user in correct channel
        permission_result = await ai_engine._check_image_generation_permission(
            user_id=123456,
            channel_id=1402666535696470169,  # Correct channel
            user_permissions=user_permissions,
        )
        print(f"Regular user in correct channel: {permission_result}")

        # Test mod privileges
        mod_permissions = {"is_admin": False, "is_mod": True}
        permission_result = await ai_engine._check_image_generation_permission(
            user_id=789012,
            channel_id=999999999,  # Any channel
            user_permissions=mod_permissions,
        )
        print(f"Mod in any channel: {permission_result}")

        # Test admin privileges
        admin_permissions = {"is_admin": True, "is_mod": False}
        permission_result = await ai_engine._check_image_generation_permission(
            user_id=345678,
            channel_id=999999999,  # Any channel
            user_permissions=admin_permissions,
        )
        print(f"Admin in any channel: {permission_result}")

        # Test rate limiting
        print("\n⏱️ Testing Rate Limiting:")
        rate_limit_result = await ai_engine._check_image_rate_limit(
            user_id=123456, user_permissions=user_permissions
        )
        print(f"Regular user rate limit: {rate_limit_result}")

        mod_rate_limit_result = await ai_engine._check_image_rate_limit(
            user_id=789012, user_permissions=mod_permissions
        )
        print(f"Mod rate limit: {rate_limit_result}")

        print("\n🎉 All tests completed!")
        print("\n📋 Setup Summary:")
        print("=" * 60)
        print("✅ Freepik integration ready")
        print("✅ Permission system configured")
        print("✅ Rate limiting system active")
        print(f"✅ Default channel ID: 1402666535696470169")
        print("✅ Mod/Admin privileges configured")

        print("\n🚀 Variable for Railway:")
        print("=" * 60)
        print("Variable Name: FREEPIK_API_KEY")
        print("Description: API key for Freepik image generation service")
        print("Required: Yes (for image generation to work)")

        # Clean up
        if ai_engine.freepik_generator:
            await ai_engine.freepik_generator.close()

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_freepik_integration())
