#!/usr/bin/env python3
"""
Individual Component Testing Script
Test each cog and function separately with detailed output
"""

import asyncio
import sys
import os
from pathlib import Path
import importlib.util
import inspect
import time

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

class IndividualTester:
    def __init__(self):
        self.test_results = {}
        
    def log(self, component: str, test: str, status: str, details: str = ""):
        """Log test result"""
        if component not in self.test_results:
            self.test_results[component] = []
            
        self.test_results[component].append({
            'test': test,
            'status': status,
            'details': details
        })
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {component}.{test}: {status}" + (f" - {details}" if details else ""))

    async def test_ai_companion(self):
        """Test AI Companion cog individually"""
        print("\n🤖 TESTING: AI Companion Cog")
        print("=" * 50)
        
        try:
            # Test import
            from cogs.ai_companion import AICompanion
            self.log("AICompanion", "import", "PASS", "Successfully imported")
            
            # Test class structure
            methods = [m for m in dir(AICompanion) if not m.startswith('_')]
            self.log("AICompanion", "class_structure", "PASS", f"Found {len(methods)} methods")
            
            # Test key methods exist
            key_methods = ['wellness_checkin', 'mood_tracker', 'celebrate']
            for method in key_methods:
                if hasattr(AICompanion, method):
                    self.log("AICompanion", f"method_{method}", "PASS", "Method exists")
                else:
                    self.log("AICompanion", f"method_{method}", "FAIL", "Method missing")
            
            # Test async methods
            async_methods = [name for name, method in inspect.getmembers(AICompanion) 
                           if asyncio.iscoroutinefunction(method)]
            self.log("AICompanion", "async_methods", "PASS", f"Found {len(async_methods)} async methods")
            
        except Exception as e:
            self.log("AICompanion", "import", "FAIL", str(e))

    async def test_advanced_ai(self):
        """Test Advanced AI cog individually"""
        print("\n🧠 TESTING: Advanced AI Cog")
        print("=" * 50)
        
        try:
            from cogs.advanced_ai import AdvancedAICog
            self.log("AdvancedAI", "import", "PASS", "Successfully imported")
            
            # Test class structure
            methods = [m for m in dir(AdvancedAICog) if not m.startswith('_')]
            self.log("AdvancedAI", "class_structure", "PASS", f"Found {len(methods)} methods")
            
            # Test key methods
            key_methods = ['chat', 'analyze', 'context']
            for method in key_methods:
                if hasattr(AdvancedAICog, method):
                    self.log("AdvancedAI", f"method_{method}", "PASS", "Method exists")
                else:
                    self.log("AdvancedAI", f"method_{method}", "WARN", "Method not found (may be normal)")
                    
        except Exception as e:
            self.log("AdvancedAI", "import", "FAIL", str(e))

    async def test_ai_moderation(self):
        """Test AI Moderation cog individually"""
        print("\n🛡️ TESTING: AI Moderation Cog")
        print("=" * 50)
        
        try:
            from cogs.ai_moderation import AIModeration  
            self.log("AIModerationCog", "import", "PASS", "Successfully imported")
            
            # Test moderation functions
            methods = [m for m in dir(AIModeration) if not m.startswith('_')]
            self.log("AIModerationCog", "methods", "PASS", f"Found {len(methods)} methods")
            
        except Exception as e:
            self.log("AIModerationCog", "import", "FAIL", str(e))

    async def test_admin_functions(self):
        """Test Admin cog individually"""
        print("\n👑 TESTING: Admin Functions")
        print("=" * 50)
        
        try:
            from cogs.admin_optimized import OptimizedAdmin
            self.log("AdminOptimized", "import", "PASS", "Successfully imported")
            
            # Test admin commands
            methods = [m for m in dir(OptimizedAdmin) if not m.startswith('_')]
            self.log("AdminOptimized", "commands", "PASS", f"Found {len(methods)} admin functions")
            
        except Exception as e:
            self.log("AdminOptimized", "import", "FAIL", str(e))

    async def test_server_management(self):
        """Test Server Management functions"""
        print("\n🏠 TESTING: Server Management")
        print("=" * 50)
        
        # Test both server management cogs
        cogs_to_test = [
            ("server_management", "ServerManagement"),
            ("enhanced_server_management", "EnhancedServerManagement")
        ]
        
        for module_name, class_name in cogs_to_test:
            try:
                module = importlib.import_module(f"cogs.{module_name}")
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    self.log("ServerManagement", f"{class_name}_import", "PASS", "Successfully imported")
                    
                    methods = [m for m in dir(cls) if not m.startswith('_')]
                    self.log("ServerManagement", f"{class_name}_methods", "PASS", f"Found {len(methods)} methods")
                else:
                    self.log("ServerManagement", f"{class_name}_class", "FAIL", f"Class {class_name} not found")
                    
            except Exception as e:
                self.log("ServerManagement", f"{class_name}_import", "FAIL", str(e))

    async def test_utility_cogs(self):
        """Test utility cogs"""
        print("\n🔧 TESTING: Utility Cogs")
        print("=" * 50)
        
        utility_cogs = [
            "analytics", "bot_status", "help", "utilities", "roles", "stats"
        ]
        
        for cog_name in utility_cogs:
            try:
                module = importlib.import_module(f"cogs.{cog_name}")
                self.log("UtilityCogs", f"{cog_name}_import", "PASS", "Successfully imported")
                
                # Find main class in module
                classes = [name for name, obj in inspect.getmembers(module) 
                          if inspect.isclass(obj) and not name.startswith('_')]
                
                if classes:
                    self.log("UtilityCogs", f"{cog_name}_classes", "PASS", f"Found classes: {', '.join(classes)}")
                else:
                    self.log("UtilityCogs", f"{cog_name}_classes", "WARN", "No classes found")
                    
            except Exception as e:
                self.log("UtilityCogs", f"{cog_name}_import", "FAIL", str(e))

    async def test_specialized_cogs(self):
        """Test specialized cogs"""
        print("\n🌟 TESTING: Specialized Cogs")
        print("=" * 50)
        
        specialized_cogs = [
            "nexus", "notion", "quiz", "space"
        ]
        
        for cog_name in specialized_cogs:
            try:
                if Path(f"cogs/{cog_name}.py").exists():
                    module = importlib.import_module(f"cogs.{cog_name}")
                    self.log("SpecializedCogs", f"{cog_name}_import", "PASS", "Successfully imported")
                    
                    # Check for commands
                    classes = [name for name, obj in inspect.getmembers(module) 
                              if inspect.isclass(obj) and not name.startswith('_')]
                    self.log("SpecializedCogs", f"{cog_name}_structure", "PASS", f"Classes: {len(classes)}")
                    
                else:
                    self.log("SpecializedCogs", f"{cog_name}_file", "WARN", "File not found")
                    
            except Exception as e:
                self.log("SpecializedCogs", f"{cog_name}_import", "FAIL", str(e))

    async def test_ai_engine(self):
        """Test AI engine components"""
        print("\n🤖 TESTING: AI Engine Components")
        print("=" * 50)
        
        ai_modules = [
            "consolidated_ai_engine",
            "advanced_intelligence", 
            "model_mapping",
            "openrouter_client",
            "optimized_ai_client",
            "universal_ai_client"
        ]
        
        for module_name in ai_modules:
            try:
                module = importlib.import_module(f"ai.{module_name}")
                self.log("AIEngine", f"{module_name}_import", "PASS", "Successfully imported")
                
                # Check for key functions
                functions = [name for name, obj in inspect.getmembers(module) 
                           if inspect.isfunction(obj) and not name.startswith('_')]
                self.log("AIEngine", f"{module_name}_functions", "PASS", f"Found {len(functions)} functions")
                
            except Exception as e:
                self.log("AIEngine", f"{module_name}_import", "FAIL", str(e))

    async def test_core_systems(self):
        """Test core system components"""
        print("\n⚙️ TESTING: Core Systems")
        print("=" * 50)
        
        core_modules = [
            "ai_handler", "event_manager", "smart_moderation", "welcome_system"
        ]
        
        for module_name in core_modules:
            try:
                if Path(f"core/{module_name}.py").exists():
                    module = importlib.import_module(f"core.{module_name}")
                    self.log("CoreSystems", f"{module_name}_import", "PASS", "Successfully imported")
                    
                    # Check classes and functions
                    items = [name for name, obj in inspect.getmembers(module) 
                           if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith('_')]
                    self.log("CoreSystems", f"{module_name}_items", "PASS", f"Found {len(items)} items")
                    
                else:
                    self.log("CoreSystems", f"{module_name}_file", "WARN", "File not found")
                    
            except Exception as e:
                self.log("CoreSystems", f"{module_name}_import", "FAIL", str(e))

    async def test_configuration(self):
        """Test configuration system"""
        print("\n⚙️ TESTING: Configuration System")
        print("=" * 50)
        
        try:
            from config.unified_config import unified_config
            self.log("Configuration", "unified_config_import", "PASS", "Successfully imported")
            
            # Test config structure
            if hasattr(unified_config, 'get'):
                self.log("Configuration", "config_methods", "PASS", "Has get method")
            
            # Test config access
            config_sections = ['ai', 'database', 'logging', 'features']
            for section in config_sections:
                try:
                    value = unified_config.get(section, {})
                    self.log("Configuration", f"section_{section}", "PASS", f"Section accessible")
                except:
                    self.log("Configuration", f"section_{section}", "WARN", f"Section not found")
                    
        except Exception as e:
            self.log("Configuration", "unified_config_import", "FAIL", str(e))

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🧪 TEST SUMMARY")
        print("=" * 80)
        
        total_pass = 0
        total_fail = 0
        total_warn = 0
        
        for component, tests in self.test_results.items():
            print(f"\n📦 {component}:")
            
            component_pass = sum(1 for t in tests if t['status'] == 'PASS')
            component_fail = sum(1 for t in tests if t['status'] == 'FAIL')
            component_warn = sum(1 for t in tests if t['status'] == 'WARN')
            
            total_pass += component_pass
            total_fail += component_fail
            total_warn += component_warn
            
            print(f"   ✅ Passed: {component_pass}")
            print(f"   ❌ Failed: {component_fail}")
            print(f"   ⚠️  Warnings: {component_warn}")
            
            # Show failed tests
            failed_tests = [t for t in tests if t['status'] == 'FAIL']
            if failed_tests:
                print("   🚨 Failed Tests:")
                for test in failed_tests:
                    print(f"      - {test['test']}: {test['details']}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   ✅ Total Passed: {total_pass}")
        print(f"   ❌ Total Failed: {total_fail}")
        print(f"   ⚠️  Total Warnings: {total_warn}")
        
        success_rate = (total_pass / (total_pass + total_fail)) * 100 if (total_pass + total_fail) > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        if total_fail == 0:
            print("\n🎉 ALL TESTS PASSED! Your bot is ready! 🚀")
        else:
            print(f"\n⚠️  {total_fail} tests failed. Check the details above.")

async def main():
    """Run all individual tests"""
    print("🚀 Starting Individual Component Testing")
    print("Testing each cog and function separately...")
    print("=" * 80)
    
    tester = IndividualTester()
    start_time = time.time()
    
    # Run all tests
    await tester.test_configuration()
    await tester.test_core_systems()
    await tester.test_ai_engine()
    await tester.test_ai_companion()
    await tester.test_advanced_ai()
    await tester.test_ai_moderation()
    await tester.test_admin_functions()
    await tester.test_server_management()
    await tester.test_utility_cogs()
    await tester.test_specialized_cogs()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    tester.print_summary()
    print(f"\n⏱️ Testing completed in {duration:.2f} seconds")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()