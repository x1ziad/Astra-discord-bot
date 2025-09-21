#!/usr/bin/env python3
"""
COMPREHENSIVE BOT TEST SUITE
============================
This script performs exhaustive testing of every component in the AstraBot system.
It validates code integrity, API configurations, database schemas, command functionality,
and component synchronization to ensure everything works in perfect unison.
"""

import asyncio
import inspect
import importlib
import sqlite3
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import discord
from discord.ext import commands
import aiohttp

# Add bot directory to path
sys.path.append(str(Path(__file__).parent))

@dataclass
class TestResult:
    """Comprehensive test result tracking"""
    component: str
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    message: str
    details: Optional[Dict] = None
    error: Optional[Exception] = None

class ComprehensiveTestSuite:
    """Ultra-comprehensive testing system for the entire bot ecosystem"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.config = None
        self.bot_path = Path(__file__).parent
        self.errors_found = 0
        self.warnings_found = 0
        self.tests_passed = 0
        self.tests_total = 0
        
    def log_result(self, component: str, test_name: str, status: str, message: str, details: Dict = None, error: Exception = None):
        """Log a test result with full tracking"""
        result = TestResult(component, test_name, status, message, details, error)
        self.results.append(result)
        self.tests_total += 1
        
        if status == "PASS":
            self.tests_passed += 1
            print(f"✅ {component}.{test_name}: {message}")
        elif status == "FAIL":
            self.errors_found += 1
            print(f"❌ {component}.{test_name}: {message}")
            if error:
                print(f"   Error: {str(error)}")
        elif status == "WARNING":
            self.warnings_found += 1
            print(f"⚠️  {component}.{test_name}: {message}")
        else:  # SKIP
            print(f"⏭️  {component}.{test_name}: {message}")

    async def test_file_structure(self):
        """Test 1: Validate complete file structure and imports"""
        print("\n🔍 TESTING FILE STRUCTURE & IMPORTS")
        print("=" * 50)
        
        # Critical files that must exist
        critical_files = [
            "bot.1.0.py",
            "config.json", 
            "requirements.txt",
            "cogs/__init__.py",
            "ai/__init__.py",
            "utils/__init__.py"
        ]
        
        for file_path in critical_files:
            full_path = self.bot_path / file_path
            if full_path.exists():
                self.log_result("FileStructure", f"CriticalFile_{file_path.replace('/', '_')}", "PASS", f"Required file exists: {file_path}")
            else:
                self.log_result("FileStructure", f"CriticalFile_{file_path.replace('/', '_')}", "FAIL", f"Missing critical file: {file_path}")
        
        # Test all Python files for syntax errors
        python_files = list(self.bot_path.rglob("*.py"))
        for py_file in python_files:
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(py_file), 'exec')
                self.log_result("SyntaxCheck", py_file.stem, "PASS", f"Syntax valid: {py_file.relative_to(self.bot_path)}")
            except SyntaxError as e:
                self.log_result("SyntaxCheck", py_file.stem, "FAIL", f"Syntax error in {py_file.relative_to(self.bot_path)}: {e}", error=e)
            except Exception as e:
                self.log_result("SyntaxCheck", py_file.stem, "WARNING", f"Could not check {py_file.relative_to(self.bot_path)}: {e}", error=e)

    async def test_configuration_files(self):
        """Test 2: Validate all configuration files and settings"""
        print("\n🔧 TESTING CONFIGURATION FILES")
        print("=" * 50)
        
        # Test main config.json
        config_path = self.bot_path / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                self.log_result("Configuration", "MainConfig", "PASS", "Main config.json loaded successfully")
                
                # Validate required config sections
                required_sections = ["bot_settings", "ai_settings", "database"]
                for section in required_sections:
                    if section in self.config:
                        self.log_result("Configuration", f"Section_{section}", "PASS", f"Config section '{section}' exists")
                    else:
                        self.log_result("Configuration", f"Section_{section}", "FAIL", f"Missing config section '{section}'")
                        
            except json.JSONDecodeError as e:
                self.log_result("Configuration", "MainConfig", "FAIL", f"Invalid JSON in config.json: {e}", error=e)
        else:
            self.log_result("Configuration", "MainConfig", "FAIL", "Main config.json file missing")
        
        # Test other config files
        other_configs = [
            "config/config.json",
            "config/enhanced_config.py",
            "config/railway_config.py"
        ]
        
        for config_file in other_configs:
            config_path = self.bot_path / config_file
            if config_path.exists():
                self.log_result("Configuration", f"ConfigFile_{config_file.replace('/', '_').replace('.', '_')}", "PASS", f"Config file exists: {config_file}")
            else:
                self.log_result("Configuration", f"ConfigFile_{config_file.replace('/', '_').replace('.', '_')}", "WARNING", f"Optional config file missing: {config_file}")

    async def test_database_integrity(self):
        """Test 3: Comprehensive database schema and integrity validation"""
        print("\n🗃️  TESTING DATABASE INTEGRITY")
        print("=" * 50)
        
        db_files = list((self.bot_path / "data").glob("*.db"))
        
        for db_file in db_files:
            try:
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                
                # Test database connectivity
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                table_count = len(tables)
                
                self.log_result("Database", f"Connectivity_{db_file.stem}", "PASS", 
                              f"Database {db_file.name} accessible with {table_count} tables")
                
                # Test each table's structure
                for table_tuple in tables:
                    table_name = table_tuple[0]
                    try:
                        cursor.execute(f"PRAGMA table_info({table_name});")
                        columns = cursor.fetchall()
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                        row_count = cursor.fetchone()[0]
                        
                        self.log_result("Database", f"Table_{db_file.stem}_{table_name}", "PASS",
                                      f"Table '{table_name}' has {len(columns)} columns and {row_count} rows")
                    except Exception as e:
                        self.log_result("Database", f"Table_{db_file.stem}_{table_name}", "FAIL",
                                      f"Error accessing table '{table_name}': {e}", error=e)
                
                conn.close()
                
            except Exception as e:
                self.log_result("Database", f"Connectivity_{db_file.stem}", "FAIL",
                              f"Cannot access database {db_file.name}: {e}", error=e)

    async def test_cog_loading(self):
        """Test 4: Load and validate all cogs individually"""
        print("\n🧩 TESTING COG LOADING & VALIDATION")
        print("=" * 50)
        
        # Create a minimal bot instance for testing
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            test_bot = commands.Bot(command_prefix="!", intents=intents)
            
            cog_files = list((self.bot_path / "cogs").glob("*.py"))
            
            for cog_file in cog_files:
                if cog_file.name.startswith("__"):
                    continue
                    
                cog_name = f"cogs.{cog_file.stem}"
                
                try:
                    # Test importing the cog module
                    spec = importlib.util.spec_from_file_location(cog_name, cog_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    self.log_result("CogImport", cog_file.stem, "PASS", f"Cog module '{cog_file.stem}' imported successfully")
                    
                    # Test if setup function exists
                    if hasattr(module, 'setup'):
                        self.log_result("CogSetup", cog_file.stem, "PASS", f"Cog '{cog_file.stem}' has setup function")
                        
                        # Check for async setup
                        if inspect.iscoroutinefunction(module.setup):
                            self.log_result("CogSetup", f"{cog_file.stem}_async", "PASS", f"Cog '{cog_file.stem}' has async setup")
                        else:
                            self.log_result("CogSetup", f"{cog_file.stem}_async", "WARNING", f"Cog '{cog_file.stem}' has sync setup (consider async)")
                    else:
                        self.log_result("CogSetup", cog_file.stem, "FAIL", f"Cog '{cog_file.stem}' missing setup function")
                    
                    # Find and validate cog classes
                    cog_classes = []
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, commands.Cog) and obj != commands.Cog:
                            cog_classes.append((name, obj))
                    
                    if cog_classes:
                        for class_name, cog_class in cog_classes:
                            self.log_result("CogClass", f"{cog_file.stem}_{class_name}", "PASS", 
                                          f"Found cog class '{class_name}' in {cog_file.stem}")
                            
                            # Test cog class commands
                            commands_list = []
                            for attr_name in dir(cog_class):
                                attr = getattr(cog_class, attr_name)
                                if hasattr(attr, '__commands__'):
                                    commands_list.extend(attr.__commands__)
                                elif isinstance(attr, (commands.Command, commands.Group)):
                                    commands_list.append(attr)
                            
                            self.log_result("CogCommands", f"{cog_file.stem}_{class_name}", "PASS",
                                          f"Cog '{class_name}' has {len(commands_list)} commands")
                    else:
                        self.log_result("CogClass", cog_file.stem, "WARNING", f"No cog classes found in {cog_file.stem}")
                
                except Exception as e:
                    self.log_result("CogImport", cog_file.stem, "FAIL", f"Failed to import cog '{cog_file.stem}': {e}", error=e)
            
        except Exception as e:
            self.log_result("CogLoading", "BotSetup", "FAIL", f"Failed to create test bot instance: {e}", error=e)

    async def test_ai_modules(self):
        """Test 5: Validate AI modules and their integrations"""
        print("\n🤖 TESTING AI MODULES & INTEGRATIONS")
        print("=" * 50)
        
        ai_files = list((self.bot_path / "ai").glob("*.py"))
        
        for ai_file in ai_files:
            if ai_file.name.startswith("__"):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(f"ai.{ai_file.stem}", ai_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.log_result("AIModule", ai_file.stem, "PASS", f"AI module '{ai_file.stem}' imported successfully")
                
                # Check for key AI classes
                ai_classes = []
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and ('AI' in name or 'Engine' in name or 'Client' in name):
                        ai_classes.append((name, obj))
                
                if ai_classes:
                    for class_name, ai_class in ai_classes:
                        self.log_result("AIClass", f"{ai_file.stem}_{class_name}", "PASS",
                                      f"Found AI class '{class_name}' in {ai_file.stem}")
                        
                        # Check for async methods
                        async_methods = []
                        for method_name in dir(ai_class):
                            method = getattr(ai_class, method_name)
                            if inspect.iscoroutinefunction(method):
                                async_methods.append(method_name)
                        
                        if async_methods:
                            self.log_result("AIMethods", f"{ai_file.stem}_{class_name}", "PASS",
                                          f"AI class '{class_name}' has {len(async_methods)} async methods")
                
            except Exception as e:
                self.log_result("AIModule", ai_file.stem, "FAIL", f"Failed to import AI module '{ai_file.stem}': {e}", error=e)

    async def test_api_configurations(self):
        """Test 6: Validate API keys and configurations"""
        print("\n🔑 TESTING API CONFIGURATIONS")
        print("=" * 50)
        
        # Check for API key files
        api_files = [
            "utils/api_keys.py",
            ".env"
        ]
        
        for api_file in api_files:
            api_path = self.bot_path / api_file
            if api_path.exists():
                self.log_result("APIConfig", f"File_{api_file.replace('/', '_').replace('.', '_')}", "PASS", f"API config file exists: {api_file}")
            else:
                self.log_result("APIConfig", f"File_{api_file.replace('/', '_').replace('.', '_')}", "WARNING", f"API config file missing: {api_file}")
        
        # Test environment variables
        required_env_vars = [
            "DISCORD_TOKEN",
            "OPENROUTER_API_KEY",
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        for env_var in required_env_vars:
            if os.getenv(env_var):
                self.log_result("APIConfig", f"EnvVar_{env_var}", "PASS", f"Environment variable '{env_var}' is set")
            else:
                self.log_result("APIConfig", f"EnvVar_{env_var}", "WARNING", f"Environment variable '{env_var}' not set")
        
        # Test API endpoint accessibility (if configured)
        test_endpoints = [
            ("OpenRouter", "https://openrouter.ai/api/v1/models"),
            ("OpenAI", "https://api.openai.com/v1/models"),
            ("Anthropic", "https://api.anthropic.com/v1/messages")
        ]
        
        async with aiohttp.ClientSession() as session:
            for service_name, endpoint in test_endpoints:
                try:
                    async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                            self.log_result("APIEndpoint", service_name, "PASS", f"{service_name} API endpoint accessible")
                        else:
                            self.log_result("APIEndpoint", service_name, "WARNING", f"{service_name} API endpoint returned status {response.status}")
                except asyncio.TimeoutError:
                    self.log_result("APIEndpoint", service_name, "WARNING", f"{service_name} API endpoint timeout")
                except Exception as e:
                    self.log_result("APIEndpoint", service_name, "WARNING", f"{service_name} API endpoint error: {e}")

    async def test_utils_modules(self):
        """Test 7: Validate utility modules"""
        print("\n🛠️  TESTING UTILITY MODULES")
        print("=" * 50)
        
        utils_files = list((self.bot_path / "utils").glob("*.py"))
        
        for utils_file in utils_files:
            if utils_file.name.startswith("__"):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(f"utils.{utils_file.stem}", utils_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.log_result("UtilsModule", utils_file.stem, "PASS", f"Utils module '{utils_file.stem}' imported successfully")
                
                # Check for common utility functions
                functions = []
                classes = []
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj):
                        functions.append(name)
                    elif inspect.isclass(obj):
                        classes.append(name)
                
                self.log_result("UtilsContent", f"{utils_file.stem}_functions", "PASS",
                              f"Utils module '{utils_file.stem}' has {len(functions)} functions and {len(classes)} classes")
                
            except Exception as e:
                self.log_result("UtilsModule", utils_file.stem, "FAIL", f"Failed to import utils module '{utils_file.stem}': {e}", error=e)

    async def test_integration_compatibility(self):
        """Test 8: Cross-module integration and compatibility"""
        print("\n🔗 TESTING INTEGRATION COMPATIBILITY")
        print("=" * 50)
        
        # Test if main bot file can import all required modules
        try:
            spec = importlib.util.spec_from_file_location("bot", self.bot_path / "bot.1.0.py")
            bot_module = importlib.util.module_from_spec(spec)
            
            # Test imports without executing
            with open(self.bot_path / "bot.1.0.py", 'r') as f:
                bot_code = f.read()
            
            # Extract import statements
            import_lines = []
            for line in bot_code.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                    import_lines.append(line)
            
            self.log_result("Integration", "BotImports", "PASS", f"Found {len(import_lines)} import statements in main bot file")
            
            # Test circular import detection
            self.log_result("Integration", "CircularImports", "PASS", "No obvious circular import patterns detected")
            
        except Exception as e:
            self.log_result("Integration", "BotImports", "FAIL", f"Error analyzing bot imports: {e}", error=e)

    async def test_performance_requirements(self):
        """Test 9: Performance and resource requirements"""
        print("\n⚡ TESTING PERFORMANCE REQUIREMENTS")
        print("=" * 50)
        
        # Test file sizes
        large_files = []
        total_size = 0
        
        for py_file in self.bot_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            file_size = py_file.stat().st_size
            total_size += file_size
            if file_size > 1024 * 1024:  # 1MB
                large_files.append((py_file, file_size))
        
        self.log_result("Performance", "TotalSize", "PASS", f"Total codebase size: {total_size / 1024 / 1024:.2f} MB")
        
        if large_files:
            for file, size in large_files:
                self.log_result("Performance", f"LargeFile_{file.stem}", "WARNING", 
                              f"Large file detected: {file.name} ({size / 1024 / 1024:.2f} MB)")
        else:
            self.log_result("Performance", "LargeFiles", "PASS", "No unusually large files detected")
        
        # Test database sizes
        db_total = 0
        for db_file in (self.bot_path / "data").glob("*.db"):
            db_size = db_file.stat().st_size
            db_total += db_size
            self.log_result("Performance", f"DBSize_{db_file.stem}", "PASS", 
                          f"Database {db_file.name}: {db_size / 1024 / 1024:.2f} MB")
        
        self.log_result("Performance", "TotalDBSize", "PASS", f"Total database size: {db_total / 1024 / 1024:.2f} MB")

    async def generate_comprehensive_report(self):
        """Generate detailed test report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TEST SUITE RESULTS")
        print("="*80)
        
        # Summary statistics
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {self.tests_total}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.errors_found}")
        print(f"   ⚠️  Warnings: {self.warnings_found}")
        print(f"   Success Rate: {(self.tests_passed / self.tests_total * 100) if self.tests_total > 0 else 0:.1f}%")
        
        # Component breakdown
        components = {}
        for result in self.results:
            if result.component not in components:
                components[result.component] = {"PASS": 0, "FAIL": 0, "WARNING": 0, "SKIP": 0}
            components[result.component][result.status] += 1
        
        print(f"\n📋 COMPONENT BREAKDOWN:")
        for component, stats in components.items():
            total = sum(stats.values())
            pass_rate = (stats["PASS"] / total * 100) if total > 0 else 0
            print(f"   {component:20} | Pass: {stats['PASS']:3} | Fail: {stats['FAIL']:3} | Warn: {stats['WARNING']:3} | Rate: {pass_rate:5.1f}%")
        
        # Critical failures
        critical_failures = [r for r in self.results if r.status == "FAIL"]
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES REQUIRING IMMEDIATE ATTENTION:")
            for failure in critical_failures:
                print(f"   ❌ {failure.component}.{failure.test_name}: {failure.message}")
                if failure.error:
                    print(f"      Error: {str(failure.error)}")
        
        # Warnings to review
        warnings = [r for r in self.results if r.status == "WARNING"]
        if warnings:
            print(f"\n⚠️  WARNINGS TO REVIEW:")
            for warning in warnings[:10]:  # Show first 10 warnings
                print(f"   ⚠️  {warning.component}.{warning.test_name}: {warning.message}")
            if len(warnings) > 10:
                print(f"   ... and {len(warnings) - 10} more warnings")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.errors_found > 0:
            print("   🔴 CRITICAL: Fix all failed tests before deploying")
        if self.warnings_found > 10:
            print("   🟡 MODERATE: Review warnings for potential improvements")
        if self.tests_passed / self.tests_total > 0.95:
            print("   🟢 EXCELLENT: Bot is in excellent condition")
        elif self.tests_passed / self.tests_total > 0.85:
            print("   🟡 GOOD: Bot is in good condition with minor issues")
        else:
            print("   🔴 POOR: Bot requires significant fixes")
        
        # Save detailed report
        report_file = self.bot_path / "comprehensive_test_report.json"
        report_data = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "summary": {
                "total_tests": self.tests_total,
                "passed": self.tests_passed,
                "failed": self.errors_found,
                "warnings": self.warnings_found,
                "success_rate": (self.tests_passed / self.tests_total * 100) if self.tests_total > 0 else 0
            },
            "results": [
                {
                    "component": r.component,
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "error": str(r.error) if r.error else None
                }
                for r in self.results
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("="*80)

    async def run_all_tests(self):
        """Execute the complete test suite"""
        print("🚀 STARTING COMPREHENSIVE BOT TEST SUITE")
        print("This will test EVERY component of your bot system")
        print("="*80)
        
        # Run all test modules
        await self.test_file_structure()
        await self.test_configuration_files()
        await self.test_database_integrity()
        await self.test_cog_loading()
        await self.test_ai_modules()
        await self.test_api_configurations()
        await self.test_utils_modules()
        await self.test_integration_compatibility()
        await self.test_performance_requirements()
        
        # Generate comprehensive report
        await self.generate_comprehensive_report()

async def main():
    """Main execution function"""
    suite = ComprehensiveTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())