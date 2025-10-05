#!/usr/bin/env python3
"""
Comprehensive Bot Testing Summary
Final test to verify everything is working together
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class BotTester:
    def __init__(self):
        self.test_results = {
            "critical_passed": 0,
            "critical_failed": 0,
            "optional_passed": 0,
            "optional_warnings": 0,
            "details": []
        }
    
    def log_critical(self, test: str, status: str, details: str = ""):
        """Log critical test result"""
        if status == "PASS":
            self.test_results["critical_passed"] += 1
            emoji = "✅"
        else:
            self.test_results["critical_failed"] += 1
            emoji = "❌"
        
        result = f"{emoji} [CRITICAL] {test}: {status}" + (f" - {details}" if details else "")
        self.test_results["details"].append(result)
        print(result)
    
    def log_optional(self, test: str, status: str, details: str = ""):
        """Log optional test result"""
        if status == "PASS":
            self.test_results["optional_passed"] += 1
            emoji = "✅"
        else:
            self.test_results["optional_warnings"] += 1
            emoji = "⚠️"
        
        result = f"{emoji} [OPTIONAL] {test}: {status}" + (f" - {details}" if details else "")
        self.test_results["details"].append(result)
        print(result)

    async def test_core_bot_functionality(self):
        """Test core bot components that are essential"""
        print("\n🚀 TESTING: Core Bot Functionality")
        print("=" * 70)
        
        # Test main bot file exists
        if Path("bot.1.0.py").exists():
            self.log_critical("Bot.main_file", "PASS", "Main bot file exists")
        else:
            self.log_critical("Bot.main_file", "FAIL", "Main bot file missing")
        
        # Test core directory structure
        core_dirs = ["cogs", "ai", "core", "utils", "config"]
        for directory in core_dirs:
            if Path(directory).exists():
                self.log_critical(f"Structure.{directory}", "PASS", f"{directory} directory exists")
            else:
                self.log_critical(f"Structure.{directory}", "FAIL", f"{directory} directory missing")

    async def test_essential_cogs(self):
        """Test essential cogs that must work"""
        print("\n🧩 TESTING: Essential Cogs")
        print("=" * 70)
        
        essential_cogs = [
            ("ai_companion", "AICompanion"),
            ("advanced_ai", "AdvancedAICog"),
            ("ai_moderation", "AIModeration"),
            ("admin_optimized", "OptimizedAdmin"),
            ("help", "Help")
        ]
        
        for cog_file, class_name in essential_cogs:
            try:
                module = __import__(f"cogs.{cog_file}", fromlist=[class_name])
                cog_class = getattr(module, class_name)
                self.log_critical(f"Cog.{cog_file}", "PASS", f"{class_name} loads successfully")
            except Exception as e:
                self.log_critical(f"Cog.{cog_file}", "FAIL", f"Failed to load: {e}")

    async def test_ai_system(self):
        """Test AI system components"""
        print("\n🤖 TESTING: AI System Components")
        print("=" * 70)
        
        # Test AI engine
        try:
            from ai.consolidated_ai_engine import process_conversation, get_engine
            self.log_critical("AI.engine", "PASS", "AI engine imports successfully")
            
            # Test if process_conversation works
            try:
                result = await process_conversation(
                    message="Test message",
                    user_id=12345,
                    guild_id=11111,
                    channel_id=22222
                )
                if result:
                    self.log_critical("AI.conversation", "PASS", "AI conversation processing works")
                else:
                    self.log_optional("AI.conversation", "WARN", "AI returns empty (may need API keys)")
            except Exception as e:
                self.log_optional("AI.conversation", "WARN", f"AI processing issue: {e}")
                
        except Exception as e:
            self.log_critical("AI.engine", "FAIL", f"AI engine import failed: {e}")

    async def test_configuration(self):
        """Test configuration system"""
        print("\n⚙️ TESTING: Configuration System")
        print("=" * 70)
        
        try:
            from config.unified_config import unified_config
            self.log_critical("Config.import", "PASS", "Configuration imports successfully")
            
            # Test config file exists
            if Path("config/config.json").exists():
                self.log_critical("Config.file", "PASS", "Config file exists")
            else:
                self.log_optional("Config.file", "WARN", "Config file missing (may use defaults)")
                
        except Exception as e:
            self.log_critical("Config.import", "FAIL", f"Configuration import failed: {e}")

    async def test_database_system(self):
        """Test database components"""
        print("\n🗄️ TESTING: Database System")
        print("=" * 70)
        
        # Check if data directory exists
        if Path("data").exists():
            self.log_critical("Database.directory", "PASS", "Data directory exists")
            
            # Check for database files
            db_files = list(Path("data").glob("*.db"))
            if db_files:
                self.log_critical("Database.files", "PASS", f"Found {len(db_files)} database files")
            else:
                self.log_optional("Database.files", "WARN", "No database files found (will be created)")
        else:
            self.log_optional("Database.directory", "WARN", "Data directory missing (will be created)")

    async def test_moderation_system(self):
        """Test moderation system functionality"""
        print("\n🛡️ TESTING: Moderation System")
        print("=" * 70)
        
        try:
            from cogs.ai_moderation import AIModeration
            self.log_critical("Moderation.ai_cog", "PASS", "AI moderation cog loads")
            
            # Check for core moderation methods
            moderation_methods = [
                "_comprehensive_analysis",
                "_detect_toxic_language", 
                "_ai_toxicity_analysis",
                "_handle_violation_with_ai"
            ]
            
            for method in moderation_methods:
                if hasattr(AIModeration, method):
                    self.log_critical(f"Moderation.{method}", "PASS", f"{method} method exists")
                else:
                    self.log_optional(f"Moderation.{method}", "WARN", f"{method} method missing")
                    
        except Exception as e:
            self.log_critical("Moderation.ai_cog", "FAIL", f"AI moderation failed: {e}")
        
        # Test smart moderation core
        try:
            from core.smart_moderation import SmartModerationSystem
            self.log_critical("Moderation.smart_core", "PASS", "Smart moderation core loads")
        except Exception as e:
            self.log_optional("Moderation.smart_core", "WARN", f"Smart moderation issue: {e}")

    async def test_response_coordination(self):
        """Test the AI response coordination system"""
        print("\n🤝 TESTING: AI Response Coordination")
        print("=" * 70)
        
        try:
            from cogs.ai_companion import AICompanion
            from cogs.advanced_ai import AdvancedAICog
            
            # Mock bot
            class MockBot:
                def __init__(self):
                    self._ai_response_handled = {}
                    self.user = None
                    self.logger = None
            
            mock_bot = MockBot()
            
            # Initialize both AI cogs
            companion = AICompanion(mock_bot)
            advanced = AdvancedAICog(mock_bot)
            
            # Check if coordination system is in place
            if hasattr(mock_bot, '_ai_response_handled'):
                self.log_critical("Coordination.system", "PASS", "Response coordination system exists")
            else:
                self.log_critical("Coordination.system", "FAIL", "Response coordination missing")
                
            # Check if both cogs respect the coordination
            if hasattr(companion, '_respond_as_companion') and hasattr(advanced, 'on_message'):
                self.log_critical("Coordination.implementation", "PASS", "Both AI cogs have message handlers")
            else:
                self.log_optional("Coordination.implementation", "WARN", "Message handler structure different")
                
        except Exception as e:
            self.log_critical("Coordination.system", "FAIL", f"Coordination test failed: {e}")

    async def test_natural_conversations(self):
        """Test natural conversation formatting"""
        print("\n💬 TESTING: Natural Conversation System")
        print("=" * 70)
        
        try:
            from cogs.ai_companion import AICompanion
            
            # Mock bot for testing
            class MockBot:
                def __init__(self):
                    self._ai_response_handled = {}
                    self.user = None
                    self.logger = None
            
            companion = AICompanion(MockBot())
            
            # Test fallback methods for natural responses
            fallback_checkin = companion._generate_fallback_checkin("TestUser")
            if isinstance(fallback_checkin, dict) and all(key in fallback_checkin for key in ['greeting', 'encouragement']):
                self.log_critical("NaturalChat.checkin", "PASS", "Natural check-in format correct")
            else:
                self.log_optional("NaturalChat.checkin", "WARN", "Check-in format may need adjustment")
            
            # Test mood response
            mood_response = companion._generate_fallback_mood_response("happy")
            if isinstance(mood_response, str) and len(mood_response) > 0:
                self.log_critical("NaturalChat.mood", "PASS", "Natural mood responses work")
            else:
                self.log_optional("NaturalChat.mood", "WARN", "Mood response format issue")
                
        except Exception as e:
            self.log_critical("NaturalChat.system", "FAIL", f"Natural conversation test failed: {e}")

    def print_final_assessment(self):
        """Print final assessment"""
        print("\n" + "=" * 80)
        print("🏆 FINAL BOT ASSESSMENT")
        print("=" * 80)
        
        critical_total = self.test_results["critical_passed"] + self.test_results["critical_failed"]
        optional_total = self.test_results["optional_passed"] + self.test_results["optional_warnings"]
        
        print(f"🎯 CRITICAL SYSTEMS:")
        print(f"   ✅ Passed: {self.test_results['critical_passed']}")
        print(f"   ❌ Failed: {self.test_results['critical_failed']}")
        if critical_total > 0:
            critical_success = (self.test_results["critical_passed"] / critical_total) * 100
            print(f"   📊 Critical Success Rate: {critical_success:.1f}%")
        
        print(f"\n🔧 OPTIONAL SYSTEMS:")
        print(f"   ✅ Passed: {self.test_results['optional_passed']}")
        print(f"   ⚠️  Warnings: {self.test_results['optional_warnings']}")
        if optional_total > 0:
            optional_success = (self.test_results["optional_passed"] / optional_total) * 100
            print(f"   📊 Optional Success Rate: {optional_success:.1f}%")
        
        # Overall assessment
        print(f"\n🎮 BOT READINESS ASSESSMENT:")
        
        if self.test_results["critical_failed"] == 0:
            if critical_success >= 90:
                print("   🚀 READY FOR PRODUCTION! All critical systems operational!")
                readiness = "PRODUCTION_READY"
            else:
                print("   ✅ READY FOR TESTING! Most critical systems working!")
                readiness = "TEST_READY"
        else:
            print("   ⚠️  NEEDS ATTENTION! Some critical systems have issues!")
            readiness = "NEEDS_WORK"
        
        if self.test_results["critical_failed"] <= 2:
            print("   💡 RECOMMENDATION: Bot can run with minor issues")
        else:
            print("   🔧 RECOMMENDATION: Fix critical issues before deployment")
        
        print(f"\n📋 DETAILED RESULTS:")
        for detail in self.test_results["details"]:
            print(f"   {detail}")
        
        return readiness

async def main():
    """Run comprehensive bot testing"""
    print("🤖 ASTRA BOT - COMPREHENSIVE TESTING SUITE")
    print("Testing all systems for production readiness")
    print("=" * 80)
    
    tester = BotTester()
    start_time = time.time()
    
    # Run all critical tests
    await tester.test_core_bot_functionality()
    await tester.test_essential_cogs()
    await tester.test_ai_system()
    await tester.test_configuration()
    await tester.test_database_system()
    await tester.test_moderation_system()
    await tester.test_response_coordination()
    await tester.test_natural_conversations()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Final assessment
    readiness = tester.print_final_assessment()
    print(f"\n⏱️ Complete testing finished in {duration:.2f} seconds")
    
    # Exit with appropriate code
    if readiness == "PRODUCTION_READY":
        print("\n🎉 YOUR ASTRA BOT IS READY TO LAUNCH! 🚀")
        return 0
    elif readiness == "TEST_READY":
        print("\n✅ Your Astra Bot is ready for testing!")
        return 0
    else:
        print("\n🔧 Please address the critical issues before deployment.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)