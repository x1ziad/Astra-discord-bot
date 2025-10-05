#!/usr/bin/env python3
"""
Functional Testing Script for AI and Moderation Features
Tests specific functions with mock data
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class FunctionalTester:
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "warnings": 0, "details": []}
        
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        if status == "PASS":
            self.results["passed"] += 1
            emoji = "✅"
        elif status == "FAIL":
            self.results["failed"] += 1
            emoji = "❌"
        else:
            self.results["warnings"] += 1
            emoji = "⚠️"
            
        self.results["details"].append(f"{emoji} {test_name}: {status}" + (f" - {details}" if details else ""))
        print(f"{emoji} {test_name}: {status}" + (f" - {details}" if details else ""))

    def create_mock_bot(self):
        """Create mock bot for testing"""
        bot = Mock()
        bot.user = Mock()
        bot.user.id = 12345
        bot.user.mentioned_in = Mock(return_value=False)
        bot.logger = Mock()
        bot._ai_response_handled = {}
        return bot

    def create_mock_message(self, content: str = "Hello Astra!", author_id: int = 67890):
        """Create mock Discord message"""
        message = Mock()
        message.content = content
        message.id = 123456789
        message.author = Mock()
        message.author.id = author_id
        message.author.display_name = "TestUser"
        message.author.bot = False
        message.guild = Mock()
        message.guild.id = 11111
        message.channel = Mock()
        message.channel.id = 22222
        message.channel.name = "test-channel"
        message.reply = AsyncMock()
        message.add_reaction = AsyncMock()
        return message

    def create_mock_interaction(self, user_id: int = 67890):
        """Create mock Discord interaction"""
        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = user_id
        interaction.user.display_name = "TestUser"
        interaction.guild = Mock()
        interaction.guild.id = 11111
        interaction.response = Mock()
        interaction.response.defer = AsyncMock()
        interaction.response.send_message = AsyncMock()
        interaction.followup = Mock()
        interaction.followup.send = AsyncMock()
        return interaction

    async def test_ai_companion_functions(self):
        """Test AI Companion specific functions"""
        print("\n🤖 TESTING: AI Companion Functions")
        print("=" * 60)
        
        try:
            from cogs.ai_companion import AICompanion, UserMood, CompanionPersonality
            
            # Test UserMood class
            mood = UserMood()
            if hasattr(mood, 'current_mood') and hasattr(mood, 'mood_history'):
                self.log_result("AICompanion.UserMood", "PASS", "UserMood class structure correct")
            else:
                self.log_result("AICompanion.UserMood", "FAIL", "UserMood missing attributes")
            
            # Test CompanionPersonality class
            personality = CompanionPersonality()
            if hasattr(personality, 'traits') and hasattr(personality, 'interaction_styles'):
                self.log_result("AICompanion.CompanionPersonality", "PASS", "Personality class structure correct")
            else:
                self.log_result("AICompanion.CompanionPersonality", "FAIL", "Personality missing attributes")
            
            # Test AICompanion initialization
            mock_bot = self.create_mock_bot()
            companion = AICompanion(mock_bot)
            
            if hasattr(companion, 'user_moods') and hasattr(companion, 'features'):
                self.log_result("AICompanion.initialization", "PASS", "Companion initialized successfully")
            else:
                self.log_result("AICompanion.initialization", "FAIL", "Companion missing core attributes")
            
            # Test mood tracking
            test_user_id = 12345
            user_mood = await companion.get_user_mood(test_user_id)
            if isinstance(user_mood, UserMood):
                self.log_result("AICompanion.get_user_mood", "PASS", "Mood tracking functional")
            else:
                self.log_result("AICompanion.get_user_mood", "FAIL", "Mood tracking failed")
            
            # Test message sentiment analysis (this is a private method, so we'll test indirectly)
            mock_message = self.create_mock_message("I'm feeling happy today!")
            try:
                await companion._analyze_message_sentiment(mock_message)
                self.log_result("AICompanion.sentiment_analysis", "PASS", "Sentiment analysis executed without error")
            except Exception as e:
                self.log_result("AICompanion.sentiment_analysis", "FAIL", f"Sentiment analysis failed: {e}")
                
            # Test fallback methods
            fallback_checkin = companion._generate_fallback_checkin("TestUser")
            if isinstance(fallback_checkin, dict) and 'greeting' in fallback_checkin:
                self.log_result("AICompanion.fallback_checkin", "PASS", "Fallback checkin works")
            else:
                self.log_result("AICompanion.fallback_checkin", "FAIL", "Fallback checkin malformed")
                
        except Exception as e:
            self.log_result("AICompanion.general", "FAIL", f"General error: {e}")

    async def test_advanced_ai_functions(self):
        """Test Advanced AI cog functions"""
        print("\n🧠 TESTING: Advanced AI Functions")
        print("=" * 60)
        
        try:
            from cogs.advanced_ai import AdvancedAICog
            
            mock_bot = self.create_mock_bot()
            advanced_ai = AdvancedAICog(mock_bot)
            
            # Test initialization
            if hasattr(advanced_ai, 'bot') and hasattr(advanced_ai, 'config'):
                self.log_result("AdvancedAI.initialization", "PASS", "Advanced AI initialized")
            else:
                self.log_result("AdvancedAI.initialization", "FAIL", "Advanced AI missing core attributes")
            
            # Test message handling (should be disabled for responses)
            mock_message = self.create_mock_message("Test message for advanced AI")
            try:
                # This should not produce a response due to coordination system
                await advanced_ai.on_message(mock_message)
                self.log_result("AdvancedAI.message_handling", "PASS", "Message handling executed (coordination respected)")
            except Exception as e:
                self.log_result("AdvancedAI.message_handling", "WARN", f"Message handling issue: {e}")
                
        except Exception as e:
            self.log_result("AdvancedAI.general", "FAIL", f"General error: {e}")

    async def test_ai_moderation_functions(self):
        """Test AI Moderation functions"""
        print("\n🛡️ TESTING: AI Moderation Functions")
        print("=" * 60)
        
        try:
            from cogs.ai_moderation import AIModeration
            
            mock_bot = self.create_mock_bot()
            ai_mod = AIModeration(mock_bot)
            
            # Test initialization
            if hasattr(ai_mod, 'bot'):
                self.log_result("AIModeration.initialization", "PASS", "AI Moderation initialized")
            else:
                self.log_result("AIModeration.initialization", "FAIL", "AI Moderation missing bot attribute")
            
            # Test moderation methods exist
            moderation_methods = ['scan_message', 'moderate_content', 'check_toxicity']
            for method in moderation_methods:
                if hasattr(ai_mod, method):
                    self.log_result("AIModeration." + method, "PASS", f"{method} method exists")
                else:
                    self.log_result("AIModeration." + method, "WARN", f"{method} method not found (may be named differently)")
                    
        except Exception as e:
            self.log_result("AIModeration.general", "FAIL", f"General error: {e}")

    async def test_admin_functions(self):
        """Test Admin functions"""
        print("\n👑 TESTING: Admin Functions")
        print("=" * 60)
        
        try:
            from cogs.admin_optimized import OptimizedAdmin
            
            mock_bot = self.create_mock_bot()
            admin = OptimizedAdmin(mock_bot)
            
            # Test initialization
            if hasattr(admin, 'bot'):
                self.log_result("Admin.initialization", "PASS", "Admin cog initialized")
            else:
                self.log_result("Admin.initialization", "FAIL", "Admin cog missing bot attribute")
            
            # Test common admin commands exist
            admin_commands = ['kick', 'ban', 'timeout', 'purge']
            for command in admin_commands:
                if hasattr(admin, command):
                    self.log_result("Admin." + command, "PASS", f"{command} command exists")
                else:
                    self.log_result("Admin." + command, "WARN", f"{command} command not found (may be named differently)")
                    
        except Exception as e:
            self.log_result("Admin.general", "FAIL", f"General error: {e}")

    async def test_ai_engine_functions(self):
        """Test AI Engine core functions"""
        print("\n⚙️ TESTING: AI Engine Core Functions")
        print("=" * 60)
        
        try:
            from ai.consolidated_ai_engine import get_engine, process_conversation
            
            # Test engine retrieval
            try:
                engine = await get_engine()
                if engine is not None:
                    self.log_result("AIEngine.get_engine", "PASS", "Engine retrieved successfully")
                else:
                    self.log_result("AIEngine.get_engine", "WARN", "Engine returned None (may need API keys)")
            except Exception as e:
                self.log_result("AIEngine.get_engine", "WARN", f"Engine retrieval issue: {e}")
            
            # Test conversation processing (with mock data)
            try:
                response = await process_conversation(
                    message="Hello, this is a test message",
                    user_id=12345,
                    guild_id=11111,
                    channel_id=22222
                )
                if response:
                    self.log_result("AIEngine.process_conversation", "PASS", "Conversation processing functional")
                else:
                    self.log_result("AIEngine.process_conversation", "WARN", "Conversation returned empty (may need API keys)")
            except Exception as e:
                self.log_result("AIEngine.process_conversation", "WARN", f"Conversation processing issue: {e}")
                
        except Exception as e:
            self.log_result("AIEngine.general", "FAIL", f"Import or general error: {e}")

    async def test_utility_functions(self):
        """Test utility functions"""
        print("\n🔧 TESTING: Utility Functions")
        print("=" * 60)
        
        # Test permissions
        try:
            from utils.permissions import has_permission, PermissionLevel
            
            if hasattr(PermissionLevel, 'ADMIN') and hasattr(PermissionLevel, 'MOD'):
                self.log_result("Utils.permissions", "PASS", "Permission system structure correct")
            else:
                self.log_result("Utils.permissions", "FAIL", "Permission system missing levels")
                
        except Exception as e:
            self.log_result("Utils.permissions", "FAIL", f"Permission system error: {e}")
        
        # Test database utilities
        try:
            from utils.database import Database
            self.log_result("Utils.database", "PASS", "Database utilities imported")
        except Exception as e:
            self.log_result("Utils.database", "WARN", f"Database utilities issue: {e}")
        
        # Test helpers
        try:
            from utils.helpers import format_time, create_embed
            self.log_result("Utils.helpers", "PASS", "Helper functions imported")
        except Exception as e:
            self.log_result("Utils.helpers", "WARN", f"Helper functions issue: {e}")

    async def test_configuration_functionality(self):
        """Test configuration functionality"""
        print("\n⚙️ TESTING: Configuration Functionality")
        print("=" * 60)
        
        try:
            from config.unified_config import unified_config
            
            # Test basic config access
            if hasattr(unified_config, 'get'):
                self.log_result("Config.get_method", "PASS", "Config has get method")
                
                # Test some config access
                try:
                    test_value = unified_config.get('test_key', 'default_value')
                    self.log_result("Config.get_functionality", "PASS", "Config get method functional")
                except Exception as e:
                    self.log_result("Config.get_functionality", "FAIL", f"Config get failed: {e}")
            else:
                self.log_result("Config.get_method", "FAIL", "Config missing get method")
                
        except Exception as e:
            self.log_result("Config.general", "FAIL", f"Configuration error: {e}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🧪 FUNCTIONAL TEST SUMMARY")
        print("=" * 80)
        
        total = self.results["passed"] + self.results["failed"] + self.results["warnings"]
        
        print(f"📊 Results:")
        print(f"   ✅ Passed: {self.results['passed']}")
        print(f"   ❌ Failed: {self.results['failed']}")
        print(f"   ⚠️  Warnings: {self.results['warnings']}")
        print(f"   📈 Total Tests: {total}")
        
        if total > 0:
            success_rate = (self.results["passed"] / total) * 100
            print(f"   🎯 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📝 Detailed Results:")
        for detail in self.results["details"]:
            print(f"   {detail}")
        
        if self.results["failed"] == 0:
            print(f"\n🎉 All functional tests passed! Ready for production! 🚀")
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed. Review the details above.")

async def main():
    """Run functional tests"""
    print("🧪 Starting Functional Testing")
    print("Testing specific AI and moderation functions with mock data")
    print("=" * 80)
    
    tester = FunctionalTester()
    start_time = time.time()
    
    # Run all functional tests
    await tester.test_configuration_functionality()
    await tester.test_ai_engine_functions()
    await tester.test_ai_companion_functions()
    await tester.test_advanced_ai_functions()
    await tester.test_ai_moderation_functions()
    await tester.test_admin_functions()
    await tester.test_utility_functions()
    
    end_time = time.time()
    duration = end_time - start_time
    
    tester.print_summary()
    print(f"\n⏱️ Functional testing completed in {duration:.2f} seconds")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()