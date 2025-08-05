#!/usr/bin/env python3
"""
Simple AI Parameter Validation Script
Tests AI engine method signatures and parameter compatibility
"""

import sys
import os
import json
import inspect
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_method_signatures():
    """Test method signatures for parameter compatibility"""
    print("🔍 Testing Method Signatures")
    print("=" * 40)
    
    try:
        # Import the AI engine directly
        from ai.consolidated_ai_engine import ConsolidatedAIEngine
        
        # Get the method signature
        engine_method = ConsolidatedAIEngine.process_conversation
        sig = inspect.signature(engine_method)
        
        print("✅ ConsolidatedAIEngine.process_conversation signature:")
        print(f"   {sig}")
        
        # Verify expected parameters
        params = sig.parameters
        expected_params = ['self', 'message', 'user_id', 'guild_id', 'channel_id', 'context_data']
        
        print("\n📋 Parameter Analysis:")
        for param_name in expected_params:
            if param_name in params:
                param = params[param_name]
                print(f"   ✅ {param_name}: {param}")
            else:
                print(f"   ❌ {param_name}: MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Method signature test failed: {e}")
        return False


def test_config_files():
    """Test configuration file structure"""
    print("\n🔍 Testing Configuration Files")
    print("=" * 40)
    
    try:
        # Test main config
        config_path = Path("config/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("✅ config/config.json loaded:")
            print(f"   - owner_id: {config.get('owner_id')}")
            print(f"   - ai_enabled: {config.get('ai_enabled')}")
            print(f"   - ai_personality: {config.get('ai_personality')}")
            print(f"   - ai_temperature: {config.get('ai_temperature')}")
            print(f"   - ai_max_tokens: {config.get('ai_max_tokens')}")
        else:
            print("❌ config/config.json not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing File Structure")
    print("=" * 40)
    
    required_files = [
        "ai/consolidated_ai_engine.py",
        "cogs/advanced_ai.py",
        "config/config.json",
        "config/enhanced_config.py",
        "config/config_manager.py"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def analyze_advanced_ai_cog():
    """Analyze the AdvancedAI cog without importing it"""
    print("\n🔍 Analyzing AdvancedAI Cog Code")
    print("=" * 40)
    
    try:
        with open("cogs/advanced_ai.py", 'r') as f:
            content = f.read()
        
        # Check for key method definitions
        checks = [
            ("_generate_ai_response method", "_generate_ai_response"),
            ("guild_id parameter", "guild_id"),
            ("channel_id parameter", "channel_id"),
            ("context_data usage", "context_data"),
            ("process_conversation call", "process_conversation"),
        ]
        
        results = []
        for check_name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {check_name}")
                results.append(True)
            else:
                print(f"   ❌ {check_name} - NOT FOUND")
                results.append(False)
        
        # Look for the specific method signature
        if "def _generate_ai_response(" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "def _generate_ai_response(" in line:
                    # Get the full method signature (might span multiple lines)
                    sig_lines = []
                    j = i
                    while j < len(lines) and (not sig_lines or not lines[j].strip().endswith(':')):
                        sig_lines.append(lines[j].strip())
                        j += 1
                    
                    print(f"\n   📝 Found method signature:")
                    for sig_line in sig_lines:
                        print(f"      {sig_line}")
                    break
        
        return all(results)
        
    except Exception as e:
        print(f"❌ AdvancedAI analysis failed: {e}")
        return False


def check_parameter_usage():
    """Check how parameters are used in the code"""
    print("\n🔍 Checking Parameter Usage")
    print("=" * 40)
    
    try:
        with open("cogs/advanced_ai.py", 'r') as f:
            content = f.read()
        
        # Look for process_conversation calls
        lines = content.split('\n')
        call_found = False
        
        for i, line in enumerate(lines):
            if "process_conversation(" in line:
                call_found = True
                print(f"   📍 Found process_conversation call at line {i+1}:")
                
                # Show context around the call
                start = max(0, i-2)
                end = min(len(lines), i+5)
                
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"   {marker}{j+1:3d}: {lines[j]}")
                
                print()
        
        if not call_found:
            print("   ❌ No process_conversation calls found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Parameter usage check failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🚀 AI Parameter Validation Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration Files", test_config_files),
        ("Method Signatures", test_method_signatures),
        ("AdvancedAI Cog Analysis", analyze_advanced_ai_cog),
        ("Parameter Usage", check_parameter_usage)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        print("🔧 Your AI parameter structure looks correct.")
    else:
        print("⚠️  Some validation tests failed.")
        print("🔍 Check the errors above for details.")
    
    # Additional recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Deploy your bot to test real AI functionality")
    print("   2. Try /ai commands in Discord to verify responses")
    print("   3. Check logs for parameter-related errors")
    print("   4. Test owner-only commands like /admin system")


if __name__ == "__main__":
    main()
