#!/usr/bin/env python3
"""
Comprehensive AI Function Tests for AstraBot
Tests all AI commands and functions to ensure they work correctly
"""

import asyncio
import os
import sys
import traceback
from datetime import datetime

# Add the project root to path
sys.path.append(".")

# Set up test environment variables
os.environ["AI_API_KEY"] = (
    "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"
)
os.environ["AI_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["AI_MODEL"] = "deepseek/deepseek-r1:nitro"
os.environ["AI_PROVIDER"] = "universal"
os.environ["AI_PROVIDER_NAME"] = "OpenRouter"

from ai.universal_ai_client import UniversalAIClient, AIResponse


class AITester:
    def __init__(self):
        self.client = UniversalAIClient()
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")

        self.test_results.append(
            {
                "test": test_name,
                "success": success,
                "details": details,
                "timestamp": datetime.now(),
            }
        )

        if success:
            self.passed += 1
        else:
            self.failed += 1

    async def test_basic_connection(self):
        """Test basic API connection"""
        try:
            result = await self.client.test_connection()
            success = result["success"]
            details = f"Response: {result.get('response', 'No response')}"
            self.log_test("Basic Connection", success, details)
            return success
        except Exception as e:
            self.log_test("Basic Connection", False, f"Error: {e}")
            return False

    async def test_simple_chat(self):
        """Test simple chat completion"""
        try:
            messages = [{"role": "user", "content": "Say hello in exactly 3 words"}]
            response = await self.client.chat_completion(messages)

            success = isinstance(response, AIResponse) and len(response.content) > 0
            details = f"Response: {response.content[:100]}..."
            self.log_test("Simple Chat Completion", success, details)
            return success
        except Exception as e:
            self.log_test("Simple Chat Completion", False, f"Error: {e}")
            return False

    async def test_generate_text(self):
        """Test text generation interface"""
        try:
            response = await self.client.generate_text(
                "What is 2+2? Answer in one sentence."
            )
            success = len(response) > 0 and isinstance(response, str)
            details = f"Response: {response[:100]}..."
            self.log_test("Generate Text", success, details)
            return success
        except Exception as e:
            self.log_test("Generate Text", False, f"Error: {e}")
            return False

    async def test_analyze_text(self):
        """Test text analysis"""
        try:
            test_text = "The quick brown fox jumps over the lazy dog."
            response = await self.client.analyze_text(test_text, "grammar")
            success = len(response) > 0 and isinstance(response, str)
            details = f"Analysis: {response[:100]}..."
            self.log_test("Analyze Text", success, details)
            return success
        except Exception as e:
            self.log_test("Analyze Text", False, f"Error: {e}")
            return False

    async def test_conversation_context(self):
        """Test conversation with context"""
        try:
            messages = [
                {"role": "user", "content": "My name is Alice"},
                {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
                {"role": "user", "content": "What is my name?"},
            ]
            response = await self.client.chat_completion(messages)
            success = "alice" in response.content.lower()
            details = f"Context test: {response.content[:100]}..."
            self.log_test("Conversation Context", success, details)
            return success
        except Exception as e:
            self.log_test("Conversation Context", False, f"Error: {e}")
            return False

    async def test_deepseek_reasoning(self):
        """Test DeepSeek R1 reasoning capabilities"""
        try:
            prompt = "If a train travels 120 miles in 2 hours, what is its average speed? Show your step-by-step reasoning."
            response = await self.client.generate_text(prompt)

            # Check if response contains reasoning indicators
            reasoning_indicators = [
                "step",
                "reasoning",
                "calculate",
                "therefore",
                "60 mph",
                "60",
            ]
            has_reasoning = any(
                indicator in response.lower() for indicator in reasoning_indicators
            )

            success = has_reasoning and len(response) > 50
            details = f"Reasoning response: {response[:150]}..."
            self.log_test("DeepSeek Reasoning", success, details)
            return success
        except Exception as e:
            self.log_test("DeepSeek Reasoning", False, f"Error: {e}")
            return False

    async def test_different_temperatures(self):
        """Test different temperature settings"""
        try:
            prompt = "Write a creative sentence about space"

            # Test low temperature (more focused)
            response1 = await self.client.generate_text(prompt, temperature=0.2)

            # Test high temperature (more creative)
            response2 = await self.client.generate_text(prompt, temperature=0.9)

            success = (
                len(response1) > 0 and len(response2) > 0 and response1 != response2
            )
            details = f"Low temp: {response1[:50]}... | High temp: {response2[:50]}..."
            self.log_test("Different Temperatures", success, details)
            return success
        except Exception as e:
            self.log_test("Different Temperatures", False, f"Error: {e}")
            return False

    async def test_token_limits(self):
        """Test token limit settings"""
        try:
            prompt = "Write a long story about a space adventure"

            # Test with small token limit
            response = await self.client.generate_text(prompt, max_tokens=50)

            # Rough estimate - should be shorter due to token limit
            success = len(response) < 500  # Approximate check
            details = f"Limited response length: {len(response)} chars"
            self.log_test("Token Limits", success, details)
            return success
        except Exception as e:
            self.log_test("Token Limits", False, f"Error: {e}")
            return False

    async def test_error_handling(self):
        """Test error handling with invalid requests"""
        try:
            # Test with invalid model
            try:
                await self.client.generate_text("Hello", model="invalid-model-123")
                success = False  # Should have failed
                details = "Should have failed with invalid model"
            except RuntimeError:
                success = True  # Expected to fail
                details = "Correctly handled invalid model error"

            self.log_test("Error Handling", success, details)
            return success
        except Exception as e:
            self.log_test("Error Handling", False, f"Unexpected error: {e}")
            return False

    async def test_status_reporting(self):
        """Test status reporting"""
        try:
            status = self.client.get_status()
            required_keys = ["provider", "available", "model", "endpoint"]

            success = all(key in status for key in required_keys)
            details = f"Status keys: {list(status.keys())}"
            self.log_test("Status Reporting", success, details)
            return success
        except Exception as e:
            self.log_test("Status Reporting", False, f"Error: {e}")
            return False

    async def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        try:
            # Create multiple concurrent requests
            tasks = []
            for i in range(3):
                task = self.client.generate_text(f"Count to {i+1}")
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if all responses are valid
            success = all(isinstance(resp, str) and len(resp) > 0 for resp in responses)
            details = f"Completed {len(responses)} concurrent requests"
            self.log_test("Concurrent Requests", success, details)
            return success
        except Exception as e:
            self.log_test("Concurrent Requests", False, f"Error: {e}")
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive AI Function Tests")
        print("=" * 60)

        tests = [
            self.test_basic_connection,
            self.test_simple_chat,
            self.test_generate_text,
            self.test_analyze_text,
            self.test_conversation_context,
            self.test_deepseek_reasoning,
            self.test_different_temperatures,
            self.test_token_limits,
            self.test_error_handling,
            self.test_status_reporting,
            self.test_multiple_concurrent_requests,
        ]

        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                traceback.print_exc()
            print()  # Add spacing between tests

        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! The AI integration is working perfectly!")
        else:
            print(f"\n⚠️  {self.failed} tests failed. Review the errors above.")

        print("\n🔧 Client Configuration:")
        status = self.client.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")


async def main():
    """Main test runner"""
    tester = AITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
