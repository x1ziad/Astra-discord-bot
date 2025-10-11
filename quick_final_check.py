#!/usr/bin/env python3
"""
Quick Final System Check
Simple validation that all optimizations are working
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(".")


async def quick_system_check():
    """Quick check of all optimized components"""
    print("🔍 Quick Final System Check")
    print("=" * 50)

    results = {}

    # 1. Check Cache Manager
    try:
        from utils.cache_manager import cache

        await cache.set("test", "works", ttl=5)
        result = await cache.get("test")
        results["cache"] = result == "works"
        print(f"✅ Cache Manager: {'WORKING' if results['cache'] else 'FAILED'}")
    except Exception as e:
        results["cache"] = False
        print(f"❌ Cache Manager: {e}")

    # 2. Check Database
    try:
        from utils.database import db

        await db.initialize()
        results["database"] = True
        print("✅ Database: WORKING")
    except Exception as e:
        results["database"] = False
        print(f"❌ Database: {e}")

    # 3. Check Lightning Optimizer
    try:
        from utils.lightning_optimizer import lightning_optimizer

        response = await lightning_optimizer.optimize_request(
            "test", {"user_id": 1, "username": "test"}, {"guild_id": 123}
        )
        results["lightning"] = len(response) > 0
        print(
            f"✅ Lightning Optimizer: {'WORKING' if results['lightning'] else 'FAILED'}"
        )
    except Exception as e:
        results["lightning"] = False
        print(f"❌ Lightning Optimizer: {e}")

    # 4. Check API Keys
    try:
        from utils.api_keys import api_manager

        summary = api_manager.get_usage_summary()
        results["api_keys"] = "total_services" in summary
        print(f"✅ API Management: {'WORKING' if results['api_keys'] else 'FAILED'}")
    except Exception as e:
        results["api_keys"] = False
        print(f"❌ API Management: {e}")

    # 5. Check HTTP Manager
    try:
        from utils.http_manager import http_manager

        await http_manager.initialize()
        results["http"] = True
        print("✅ HTTP Manager: WORKING")
    except Exception as e:
        results["http"] = False
        print(f"❌ HTTP Manager: {e}")

    # 6. Check Helpers
    try:
        from utils.helpers import format_time

        formatted = format_time(3661)
        results["helpers"] = "hour" in formatted
        print(f"✅ Helpers: {'WORKING' if results['helpers'] else 'FAILED'}")
    except Exception as e:
        results["helpers"] = False
        print(f"❌ Helpers: {e}")

    # Calculate success rate
    working_components = sum(results.values())
    total_components = len(results)
    success_rate = (working_components / total_components) * 100

    print("\n" + "=" * 50)
    print(
        f"📊 SYSTEM STATUS: {working_components}/{total_components} components working"
    )
    print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")

    if success_rate >= 90:
        print("🚀 SYSTEM STATUS: PRODUCTION READY!")
        print("   All core optimizations are working perfectly!")
    elif success_rate >= 75:
        print("⚡ SYSTEM STATUS: MOSTLY READY!")
        print("   Most optimizations working, minor issues detected.")
    else:
        print("🔧 SYSTEM STATUS: NEEDS ATTENTION")
        print("   Some optimizations need troubleshooting.")

    print("\n🎉 AstraBot Enhanced with:")
    print("   • Hybrid Caching System")
    print("   • Lightning-Fast Response Optimization")
    print("   • Advanced Database Connection Pooling")
    print("   • Secure API Key Management")
    print("   • Optimized HTTP Session Management")
    print("   • Enhanced Helper Functions")
    print("=" * 50)

    return results


if __name__ == "__main__":
    asyncio.run(quick_system_check())
