#!/usr/bin/env python3
"""
Comprehensive Astra Bot Testing Suite
Tests each cog individually and systematically
"""

import asyncio
import sys
import traceback
import importlib.util
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any
import inspect
import time

# Test results tracking
class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.details = []

    def add_pass(self, test_name: str, details: str = ""):
        self.passed += 1
        self.details.append(f"✅ {test_name}: PASSED" + (f" - {details}" if details else ""))
        print(f"✅ {test_name}: PASSED" + (f" - {details}" if details else ""))

    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"❌ {test_name}: {error}")
        self.details.append(f"❌ {test_name}: FAILED - {error}")
        print(f"❌ {test_name}: FAILED - {error}")

    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"🧪 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if self.errors:
            print(f"\n🚨 ERRORS:")
            for error in self.errors:
                print(f"   {error}")

# Initialize test results
results = TestResults()

def test_import(module_path: str, test_name: str) -> Tuple[bool, Any]:
    """Test importing a module"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        if spec is None:
            return False, "Could not create module spec"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, module
    except Exception as e:
        return False, str(e)

def test_class_initialization(module: Any, class_name: str) -> Tuple[bool, Any]:
    """Test class initialization"""
    try:
        if not hasattr(module, class_name):
            return False, f"Class {class_name} not found in module"
        
        cls = getattr(module, class_name)
        
        # Mock bot object for testing
        class MockBot:
            def __init__(self):
                self.user = None
                self.logger = logging.getLogger("test")
                self._ai_response_handled = {}
        
        mock_bot = MockBot()
        instance = cls(mock_bot)
        return True, instance
    except Exception as e:
        return False, str(e)

def get_class_methods(cls) -> List[str]:
    """Get all methods from a class"""
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
        if not name.startswith('_'):
            methods.append(name)
    
    # Also get async methods and commands
    for name in dir(cls):
        if not name.startswith('_'):
            attr = getattr(cls, name)
            if asyncio.iscoroutinefunction(attr) or hasattr(attr, '__call__'):
                if name not in methods:
                    methods.append(name)
    
    return methods

async def test_cog_functions(cog_instance: Any, cog_name: str):
    """Test individual functions in a cog"""
    methods = get_class_methods(type(cog_instance))
    
    print(f"\n🔍 Testing {cog_name} functions:")
    print("-" * 50)
    
    for method_name in methods:
        try:
            method = getattr(cog_instance, method_name)
            
            # Skip certain types of methods
            if method_name in ['cog_unload', 'setup', '__init__']:
                continue
                
            # Test if method exists and is callable
            if callable(method):
                results.add_pass(f"{cog_name}.{method_name}", "Method exists and is callable")
            else:
                results.add_fail(f"{cog_name}.{method_name}", "Method not callable")
                
        except Exception as e:
            results.add_fail(f"{cog_name}.{method_name}", f"Error accessing method: {e}")

async def test_ai_functions():
    """Test AI-specific functions"""
    print(f"\n🤖 Testing AI Functions:")
    print("-" * 50)
    
    # Test AI imports
    try:
        from ai.consolidated_ai_engine import get_engine, process_conversation
        results.add_pass("AI.consolidated_ai_engine", "Import successful")
        
        # Test engine initialization
        try:
            engine = await get_engine()
            if engine:
                results.add_pass("AI.get_engine", "Engine initialized successfully")
            else:
                results.add_fail("AI.get_engine", "Engine returned None")
        except Exception as e:
            results.add_fail("AI.get_engine", f"Engine initialization failed: {e}")
            
    except ImportError as e:
        results.add_fail("AI.consolidated_ai_engine", f"Import failed: {e}")
    
    # Test other AI modules
    ai_modules = [
        "ai.advanced_intelligence",
        "ai.model_mapping", 
        "ai.openrouter_client",
        "ai.optimized_ai_client",
        "ai.universal_ai_client",
        "ai.user_profiling"
    ]
    
    for module_name in ai_modules:
        try:
            module = importlib.import_module(module_name)
            results.add_pass(f"AI.{module_name.split('.')[-1]}", "Import successful")
        except Exception as e:
            results.add_fail(f"AI.{module_name.split('.')[-1]}", f"Import failed: {e}")

async def test_moderation_functions():
    """Test moderation-specific functions"""
    print(f"\n🛡️ Testing Moderation Functions:")
    print("-" * 50)
    
    # Test AI moderation
    success, module_or_error = test_import("cogs/ai_moderation.py", "AI Moderation")
    if success:
        results.add_pass("Moderation.ai_moderation", "Module import successful")
        
        # Test class initialization
        if hasattr(module_or_error, 'AIModerationCog'):
            success, cog_or_error = test_class_initialization(module_or_error, 'AIModerationCog')
            if success:
                results.add_pass("Moderation.AIModerationCog", "Class initialization successful")
                await test_cog_functions(cog_or_error, "AIModerationCog")
            else:
                results.add_fail("Moderation.AIModerationCog", f"Class initialization failed: {cog_or_error}")
        else:
            results.add_fail("Moderation.AIModerationCog", "AIModerationCog class not found")
    else:
        results.add_fail("Moderation.ai_moderation", f"Module import failed: {module_or_error}")
    
    # Test smart moderation core
    try:
        from core.smart_moderation import SmartModerationSystem
        results.add_pass("Moderation.smart_moderation", "Smart moderation import successful")
    except Exception as e:
        results.add_fail("Moderation.smart_moderation", f"Smart moderation import failed: {e}")

async def test_individual_cog(cog_file: str):
    """Test an individual cog"""
    cog_path = Path("cogs") / cog_file
    cog_name = cog_file.replace('.py', '')
    
    print(f"\n🧩 Testing Cog: {cog_name}")
    print("=" * 60)
    
    # Test import
    success, module_or_error = test_import(str(cog_path), cog_name)
    if not success:
        results.add_fail(f"{cog_name}.import", f"Import failed: {module_or_error}")
        return
    
    results.add_pass(f"{cog_name}.import", "Module imported successfully")
    
    # Find cog classes (usually end with 'Cog' or similar)
    cog_classes = []
    for name in dir(module_or_error):
        obj = getattr(module_or_error, name)
        if inspect.isclass(obj) and hasattr(obj, '__init__'):
            # Check if it looks like a cog class
            if any(keyword in name.lower() for keyword in ['cog', 'command', 'bot']):
                cog_classes.append(name)
    
    if not cog_classes:
        # Fallback: look for any class that takes a bot parameter
        for name in dir(module_or_error):
            obj = getattr(module_or_error, name)
            if inspect.isclass(obj):
                try:
                    sig = inspect.signature(obj.__init__)
                    params = list(sig.parameters.keys())
                    if len(params) >= 2 and 'bot' in params[1].lower():
                        cog_classes.append(name)
                except:
                    pass
    
    if not cog_classes:
        results.add_fail(f"{cog_name}.class_detection", "No cog classes found")
        return
    
    # Test each cog class
    for class_name in cog_classes:
        success, cog_or_error = test_class_initialization(module_or_error, class_name)
        if success:
            results.add_pass(f"{cog_name}.{class_name}", "Class initialization successful")
            await test_cog_functions(cog_or_error, f"{cog_name}.{class_name}")
        else:
            results.add_fail(f"{cog_name}.{class_name}", f"Class initialization failed: {cog_or_error}")

async def test_core_systems():
    """Test core system components"""
    print(f"\n⚙️ Testing Core Systems:")
    print("-" * 50)
    
    core_modules = [
        ("core/ai_handler.py", "AI Handler"),
        ("core/event_manager.py", "Event Manager"), 
        ("core/smart_moderation.py", "Smart Moderation"),
        ("core/welcome_system.py", "Welcome System")
    ]
    
    for module_path, module_name in core_modules:
        if Path(module_path).exists():
            success, module_or_error = test_import(module_path, module_name)
            if success:
                results.add_pass(f"Core.{module_name.replace(' ', '_').lower()}", "Import successful")
            else:
                results.add_fail(f"Core.{module_name.replace(' ', '_').lower()}", f"Import failed: {module_or_error}")
        else:
            results.add_fail(f"Core.{module_name.replace(' ', '_').lower()}", "File not found")

async def test_utilities():
    """Test utility modules"""
    print(f"\n🔧 Testing Utilities:")
    print("-" * 50)
    
    utils_modules = [
        "utils.database",
        "utils.helpers", 
        "utils.permissions",
        "utils.cache_manager",
        "utils.enhanced_error_handler"
    ]
    
    for module_name in utils_modules:
        try:
            module = importlib.import_module(module_name)
            results.add_pass(f"Utils.{module_name.split('.')[-1]}", "Import successful")
        except Exception as e:
            results.add_fail(f"Utils.{module_name.split('.')[-1]}", f"Import failed: {e}")

async def test_configuration():
    """Test configuration systems"""
    print(f"\n⚙️ Testing Configuration:")
    print("-" * 50)
    
    try:
        from config.unified_config import unified_config
        results.add_pass("Config.unified_config", "Import successful")
        
        # Test config structure
        if hasattr(unified_config, 'get'):
            results.add_pass("Config.unified_config.structure", "Config has get method")
        else:
            results.add_fail("Config.unified_config.structure", "Config missing get method")
            
    except Exception as e:
        results.add_fail("Config.unified_config", f"Import failed: {e}")

async def main():
    """Main testing function"""
    print("🚀 Starting Comprehensive Astra Bot Testing")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test configuration first
    await test_configuration()
    
    # Test core systems
    await test_core_systems()
    
    # Test utilities
    await test_utilities()
    
    # Test AI functions
    await test_ai_functions()
    
    # Test moderation functions
    await test_moderation_functions()
    
    # Test each cog individually
    cog_files = [
        "ai_companion.py",
        "advanced_ai.py", 
        "ai_moderation.py",
        "admin_optimized.py",
        "analytics.py",
        "bot_setup_enhanced.py",
        "bot_status.py",
        "enhanced_server_management.py",
        "help.py",
        "nexus.py",
        "notion.py",
        "quiz.py",
        "roles.py",
        "server_management.py",
        "space.py",
        "stats.py",
        "utilities.py"
    ]
    
    for cog_file in cog_files:
        if Path(f"cogs/{cog_file}").exists():
            await test_individual_cog(cog_file)
        else:
            results.add_fail(f"Cog.{cog_file}", "File not found")
    
    # Print final results
    end_time = time.time()
    duration = end_time - start_time
    
    results.print_summary()
    print(f"\n⏱️ Testing completed in {duration:.2f} seconds")
    
    # Exit with appropriate code
    if results.failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Your bot is ready to rock! 🚀")
        sys.exit(0)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing
    
    # Run the tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
        results.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Fatal testing error: {e}")
        traceback.print_exc()
        sys.exit(1)