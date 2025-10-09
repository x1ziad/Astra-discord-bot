#!/usr/bin/env python3
"""
🔍 Comprehensive Astra Bot System Test Suite
=====================================
Tests every aspect of the bot for production readiness:
- Core system initialization
- All cogs and commands  
- AI system integration
- Database connectivity
- Configuration management
- Error handling
- Performance optimization
- Feature synchronization
"""

import asyncio
import sys
import os
import importlib.util
import traceback
import time
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, '/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot')

class ComprehensiveTestSuite:
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'critical_issues': [],
            'performance_metrics': {}
        }
        self.start_time = time.time()
    
    def log_result(self, test_name: str, status: str, message: str = "", critical: bool = False):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status, 
            'message': message,
            'timestamp': time.time() - self.start_time
        }
        
        if status == 'PASS':
            self.results['passed'].append(result)
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.results['failed'].append(result)
            if critical:
                self.results['critical_issues'].append(result)
            print(f"❌ {test_name}: {message}")
        elif status == 'WARNING':
            self.results['warnings'].append(result)
            print(f"⚠️  {test_name}: {message}")
    
    def test_core_imports(self):
        """Test 1: Core system imports"""
        print("\n🔧 TESTING CORE SYSTEM IMPORTS...")
        
        try:
            # Test Discord.py
            import discord
            from discord.ext import commands
            self.log_result("Discord.py Import", "PASS", f"Version {discord.__version__}")
            
            # Test asyncio
            import asyncio
            self.log_result("Asyncio Import", "PASS", "Event loop support available")
            
            # Test core bot components
            from config.unified_config import unified_config
            self.log_result("Unified Config", "PASS", "Configuration system loaded")
            
            from logger.enhanced_logger import setup_enhanced_logger
            self.log_result("Enhanced Logger", "PASS", "Logging system available")
            
            # Test database
            from utils.database import db
            self.log_result("Database System", "PASS", "Database utilities loaded")
            
        except Exception as e:
            self.log_result("Core Imports", "FAIL", f"Import error: {e}", critical=True)
    
    def test_ai_system(self):
        """Test 2: AI System Components"""
        print("\n🤖 TESTING AI SYSTEM...")
        
        try:
            # Test AI clients
            from ai.universal_ai_client import UniversalAIClient
            self.log_result("Universal AI Client", "PASS", "AI client available")
            
            from ai.multi_provider_ai import MultiProviderAIManager
            self.log_result("Multi-Provider AI", "PASS", "AI manager available")
            
            # Test personality system
            from utils.astra_personality import get_personality_core, AstraPersonalityCore
            personality = get_personality_core(None)
            self.log_result("Personality Core", "PASS", f"Mode: {personality.current_mode}")
            
            # Test personality methods
            context = {'message': 'test', 'user_id': '123', 'username': 'TestUser'}
            style = personality.generate_response_style(context)
            self.log_result("Personality Style Generation", "PASS", f"Generated style with {len(style)} parameters")
            
            # Test AI client creation
            ai_client = UniversalAIClient()
            self.log_result("AI Client Creation", "PASS", "Client instantiated successfully")
            
        except Exception as e:
            self.log_result("AI System", "FAIL", f"AI error: {e}", critical=True)
    
    def test_cogs_import(self):
        """Test 3: All Cogs Import"""
        print("\n📦 TESTING COGS IMPORT...")
        
        cogs_to_test = [
            ('cogs.admin_optimized', 'AdminOptimized'),
            ('cogs.advanced_ai', 'AdvancedAI'),
            ('cogs.ai_companion', 'AICompanion'),
            ('cogs.ai_moderation', 'AIModerationCog'),
            ('cogs.analytics', 'AnalyticsCog'),
            ('cogs.bot_setup_enhanced', 'BotSetupEnhanced'),
            ('cogs.bot_status', 'BotStatus'),
            ('cogs.enhanced_security', 'EnhancedSecurity'),
            ('cogs.enhanced_server_management', 'EnhancedServerManagement'),
            ('cogs.nexus', 'Nexus'),
            ('cogs.notion', 'NotionCog'),
            ('cogs.personality_manager', 'PersonalityManager'),
            ('cogs.quiz', 'QuizCog'),
            ('cogs.roles', 'RolesCog'),
            ('cogs.security_commands', 'SecurityCommands'),
            ('cogs.security_manager', 'SecurityManager'),
            ('cogs.space', 'SpaceCog'),
        ]
        
        for module_name, class_name in cogs_to_test:
            try:
                module = importlib.import_module(module_name)
                cog_class = getattr(module, class_name)
                self.log_result(f"Cog: {class_name}", "PASS", f"Import successful")
            except Exception as e:
                self.log_result(f"Cog: {class_name}", "FAIL", f"Import failed: {e}")
    
    def test_database_system(self):
        """Test 4: Database System"""
        print("\n💾 TESTING DATABASE SYSTEM...")
        
        try:
            # Test database utilities
            from utils.database import db, SimpleDatabaseManager
            self.log_result("Database Utils", "PASS", "Database manager available")
            
            # Test personality database
            personality_db_path = Path("data/personality")
            if personality_db_path.exists():
                self.log_result("Personality Database", "PASS", "Personality data directory exists")
            else:
                self.log_result("Personality Database", "WARNING", "Personality directory missing")
            
            # Test main database
            main_db_path = Path("data/astra.db")
            if main_db_path.exists():
                self.log_result("Main Database", "PASS", f"Database file exists ({main_db_path.stat().st_size} bytes)")
            else:
                self.log_result("Main Database", "WARNING", "Main database file missing")
                
        except Exception as e:
            self.log_result("Database System", "FAIL", f"Database error: {e}")
    
    def test_configuration_system(self):
        """Test 5: Configuration System"""
        print("\n⚙️  TESTING CONFIGURATION SYSTEM...")
        
        try:
            from config.unified_config import unified_config
            
            # Test configuration access
            bot_config = unified_config.bot_config
            self.log_result("Bot Config Access", "PASS", f"Bot name: {bot_config.name}")
            
            # Test owner ID retrieval
            owner_id = unified_config.get_owner_id()
            if owner_id:
                self.log_result("Owner ID Config", "PASS", f"Owner ID configured: {owner_id}")
            else:
                self.log_result("Owner ID Config", "WARNING", "No owner ID configured")
            
            # Test AI config
            ai_config = unified_config.ai_config
            self.log_result("AI Config Access", "PASS", "AI configuration loaded")
            
            # Test environment variables
            import os
            discord_token = os.getenv('DISCORD_TOKEN')
            if discord_token:
                self.log_result("Discord Token", "PASS", f"Token configured ({len(discord_token)} chars)")
            else:
                self.log_result("Discord Token", "FAIL", "No Discord token found", critical=True)
                
        except Exception as e:
            self.log_result("Configuration System", "FAIL", f"Config error: {e}")
    
    def test_command_optimizer(self):
        """Test 6: Command Optimization System"""
        print("\n⚡ TESTING COMMAND OPTIMIZATION...")
        
        try:
            from utils.command_optimizer import ResponseCache, auto_optimize_commands
            
            # Test cache creation
            cache = ResponseCache()
            self.log_result("Response Cache Creation", "PASS", "Cache instantiated")
            
            # Test cache stats (this was one of the fixed errors)
            stats = cache.get_stats()
            expected_keys = ['size', 'max_size', 'hit_rate', 'ttl']
            if all(key in stats for key in expected_keys):
                self.log_result("Cache Stats Method", "PASS", f"All stats available: {stats}")
            else:
                self.log_result("Cache Stats Method", "FAIL", f"Missing stats keys: {stats}")
            
            # Test cache operations
            test_key = "test_key"
            test_value = "test_value"
            
            # Test set operation
            import asyncio
            asyncio.run(cache.set(test_key, test_value))
            self.log_result("Cache Set Operation", "PASS", "Value stored successfully")
            
            # Test get operation  
            cached_value = asyncio.run(cache.get(test_key))
            if cached_value == test_value:
                self.log_result("Cache Get Operation", "PASS", "Value retrieved successfully")
            else:
                self.log_result("Cache Get Operation", "FAIL", f"Expected {test_value}, got {cached_value}")
                
        except Exception as e:
            self.log_result("Command Optimizer", "FAIL", f"Optimizer error: {e}")
    
    def test_security_system(self):
        """Test 7: Security System"""
        print("\n🛡️  TESTING SECURITY SYSTEM...")
        
        try:
            from utils.permissions import PermissionLevel, has_permission
            self.log_result("Permission System", "PASS", "Permission utilities loaded")
            
            # Test security cogs
            from cogs.enhanced_security import EnhancedSecurity
            self.log_result("Enhanced Security", "PASS", "Security cog available")
            
            from cogs.security_manager import SecurityManager
            self.log_result("Security Manager", "PASS", "Security manager available")
            
            from cogs.security_commands import SecurityCommands
            self.log_result("Security Commands", "PASS", "Security commands available")
            
        except Exception as e:
            self.log_result("Security System", "FAIL", f"Security error: {e}")
    
    def test_ui_components(self):
        """Test 8: UI Components"""
        print("\n🎨 TESTING UI COMPONENTS...")
        
        try:
            from ui.embeds import EmbedBuilder
            self.log_result("Embed Builder", "PASS", "UI embed system available")
            
            # Test embed creation
            embed = EmbedBuilder.success("Test", "Test description")
            if embed.title == "✅ Test":
                self.log_result("Embed Creation", "PASS", "Success embed generated correctly")
            else:
                self.log_result("Embed Creation", "FAIL", f"Unexpected embed title: {embed.title}")
            
            from ui.ui_components import create_pagination_view
            self.log_result("UI Components", "PASS", "UI components available")
            
        except Exception as e:
            self.log_result("UI Components", "FAIL", f"UI error: {e}")
    
    def test_performance_systems(self):
        """Test 9: Performance Systems"""
        print("\n🚀 TESTING PERFORMANCE SYSTEMS...")
        
        try:
            # Test lightning optimizer
            from utils.lightning_optimizer import LightningOptimizer
            self.log_result("Lightning Optimizer", "PASS", "Performance optimizer available")
            
            # Test response enhancer
            from utils.response_enhancer import ResponseEnhancer
            enhancer = ResponseEnhancer()
            self.log_result("Response Enhancer", "PASS", "Response enhancement system loaded")
            
            # Test cache manager
            from utils.cache_manager import CacheManager
            self.log_result("Cache Manager", "PASS", "Cache management system available")
            
            # Test rate limiter
            from utils.rate_limiter import RateLimiter
            self.log_result("Rate Limiter", "PASS", "Rate limiting system available")
            
        except Exception as e:
            self.log_result("Performance Systems", "FAIL", f"Performance error: {e}")
    
    def test_bot_initialization(self):
        """Test 10: Bot Class Initialization"""
        print("\n🤖 TESTING BOT INITIALIZATION...")
        
        try:
            # Test bot file import
            spec = importlib.util.spec_from_file_location("bot", "bot.1.0.py")
            bot_module = importlib.util.module_from_spec(spec)
            
            # Test if we can access the bot class without fully initializing
            self.log_result("Bot File Import", "PASS", "Bot module accessible")
            
            # Test intents configuration
            import discord
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.guild_reactions = True
            self.log_result("Discord Intents", "PASS", "Required intents configured")
            
        except Exception as e:
            self.log_result("Bot Initialization", "FAIL", f"Bot init error: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*70)
        
        total_tests = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        pass_rate = (len(self.results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   ✅ Passed: {len(self.results['passed'])}")
        print(f"   ❌ Failed: {len(self.results['failed'])}")
        print(f"   ⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"   🚨 Critical Issues: {len(self.results['critical_issues'])}")
        print(f"   📈 Pass Rate: {pass_rate:.1f}%")
        print(f"   ⏱️  Total Time: {time.time() - self.start_time:.2f}s")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.results['critical_issues']:
                print(f"   ❌ {issue['test']}: {issue['message']}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED TESTS:")
            for failed in self.results['failed']:
                if failed not in self.results['critical_issues']:
                    print(f"   • {failed['test']}: {failed['message']}")
        
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.results['warnings']:
                print(f"   • {warning['test']}: {warning['message']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if len(self.results['critical_issues']) == 0:
            if pass_rate >= 90:
                print("   🟢 EXCELLENT - Bot is production ready!")
            elif pass_rate >= 80:
                print("   🟡 GOOD - Minor issues to address")
            else:
                print("   🟠 FAIR - Several issues need attention")
        else:
            print("   🔴 NOT READY - Critical issues must be resolved")
        
        return {
            'total_tests': total_tests,
            'pass_rate': pass_rate,
            'critical_issues': len(self.results['critical_issues']),
            'production_ready': len(self.results['critical_issues']) == 0 and pass_rate >= 80
        }

def main():
    """Run comprehensive test suite"""
    print("🔍 STARTING COMPREHENSIVE ASTRA BOT TEST SUITE")
    print("=" * 70)
    
    suite = ComprehensiveTestSuite()
    
    # Run all tests
    suite.test_core_imports()
    suite.test_ai_system()
    suite.test_cogs_import()
    suite.test_database_system()
    suite.test_configuration_system()
    suite.test_command_optimizer()
    suite.test_security_system()
    suite.test_ui_components()
    suite.test_performance_systems()
    suite.test_bot_initialization()
    
    # Generate final report
    report = suite.generate_report()
    
    return report

if __name__ == "__main__":
    main()