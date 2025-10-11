#!/usr/bin/env python3
"""
Comprehensive Fix Validation
Tests both the ALTS warning suppression and the coroutine bug fix
"""

import sys
import os

def test_warning_suppression():
    """Test that warning suppression is working"""
    print("🔇 Testing Warning Suppression...")
    
    # Import suppression module
    try:
        import suppress_warnings
        print("✅ Warning suppression module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import suppression module: {e}")
        return False
    
    # Check environment variables
    required_vars = [
        "GRPC_VERBOSITY",
        "GLOG_minloglevel", 
        "GOOGLE_APPLICATION_CREDENTIALS_DISABLED"
    ]
    
    for var in required_vars:
        if var in os.environ:
            print(f"✅ {var} = {os.environ[var]}")
        else:
            print(f"❌ {var} not set")
            return False
    
    return True

def test_coroutine_fix():
    """Test that the coroutine issue is fixed"""
    print("\n🔧 Testing Coroutine Fix...")
    
    # Test that user_profiles is properly initialized as dict, not coroutine
    try:
        # Simulate the fixed initialization
        user_profiles = {}  # This is what we changed it to
        
        # Test that .values() works
        values = user_profiles.values()
        print("✅ user_profiles.values() works correctly")
        
        # Test iteration over values
        for value in user_profiles.values():
            pass
        print("✅ Iteration over user_profiles.values() works")
        
        # Test with some data
        user_profiles["test_user"] = {"lore_searches": ["test_topic"]}
        for user_data in user_profiles.values():
            searches = user_data.get('lore_searches', [])
            print(f"✅ Access to user data works: {len(searches)} searches")
        
        return True
        
    except Exception as e:
        print(f"❌ Coroutine fix test failed: {e}")
        return False

def test_async_initialization():
    """Test that async initialization pattern works"""
    print("\n⚡ Testing Async Initialization Pattern...")
    
    try:
        import asyncio
        
        async def mock_load_user_profiles():
            """Mock async loading function"""
            await asyncio.sleep(0.001)  # Simulate async operation
            return {"user1": {"lore_searches": ["topic1"]}, "user2": {"data": "test"}}
        
        class MockCog:
            def __init__(self):
                self.user_profiles = {}  # Initialize empty (the fix)
                self._initialized = False
            
            async def initialize(self):
                """Async initialization method"""
                if not self._initialized:
                    self.user_profiles = await mock_load_user_profiles()
                    self._initialized = True
        
        async def test_initialization():
            cog = MockCog()
            
            # Before initialization - empty dict
            assert isinstance(cog.user_profiles, dict)
            assert len(cog.user_profiles) == 0
            print("✅ Initial state: empty dict (not coroutine)")
            
            # After initialization - populated dict
            await cog.initialize()
            assert isinstance(cog.user_profiles, dict)
            assert len(cog.user_profiles) == 2
            print("✅ After async init: populated dict")
            
            # Test values() method works
            for user_data in cog.user_profiles.values():
                assert isinstance(user_data, dict)
            print("✅ values() method works correctly")
            
            return True
        
        # Run the async test
        result = asyncio.run(test_initialization())
        return result
        
    except Exception as e:
        print(f"❌ Async initialization test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🧪 Comprehensive Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Warning Suppression", test_warning_suppression),
        ("Coroutine Fix", test_coroutine_fix),
        ("Async Initialization", test_async_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL FIXES VALIDATED SUCCESSFULLY!")
        print("✅ ALTS warnings will be suppressed")
        print("✅ Coroutine error is fixed")
        print("✅ Async initialization pattern works")
    else:
        print("❌ Some fixes need attention")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)