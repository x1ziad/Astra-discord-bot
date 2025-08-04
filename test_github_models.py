#!/usr/bin/env python3
"""
Test script for GitHub Models AI integration
Tests the DeepSeek R1-0528 model connection and performance
"""

import os
import asyncio
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_github_models():
    """Test GitHub Models integration"""
    print("🧪 Testing GitHub Models Integration")
    print("=" * 50)
    
    # Test 1: Import dependencies
    try:
        from ai.github_models_client import GitHubModelsClient, GITHUB_MODELS_AVAILABLE
        print("✅ GitHub Models client imported successfully")
        print(f"📦 Azure AI Inference available: {GITHUB_MODELS_AVAILABLE}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Check environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("💡 Set GITHUB_TOKEN in your environment to test")
        return False
    else:
        print("✅ GITHUB_TOKEN found")
    
    # Test 3: Initialize client
    try:
        client = GitHubModelsClient(
            github_token=github_token,
            openai_api_key=os.getenv("OPENAI_API_KEY")  # Optional fallback
        )
        print("✅ GitHub Models client initialized")
    except Exception as e:
        print(f"❌ Client initialization error: {e}")
        return False
    
    # Test 4: Simple chat completion
    try:
        print("\n🚀 Testing AI Response...")
        print("-" * 30)
        
        test_prompt = "Hello! Can you tell me about space exploration in exactly 2 sentences?"
        
        print(f"📝 Prompt: {test_prompt}")
        print("⏳ Waiting for response...")
        
        start_time = datetime.now()
        response = await client.chat_completion(
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.7,
            max_tokens=100
        )
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Response received in {response_time:.2f}s")
        print(f"🤖 Model: {response.model}")
        print(f"🔧 Provider: {response.provider}")
        print(f"📊 Tokens: {response.tokens_used or 'N/A'}")
        print(f"🎯 Finish Reason: {response.finish_reason or 'N/A'}")
        print(f"💬 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        return False

async def test_advanced_features():
    """Test advanced AI features"""
    print("\n🎯 Testing Advanced Features")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Skipping advanced tests - no GITHUB_TOKEN")
        return False
    
    try:
        from ai.github_models_client import GitHubModelsClient
        client = GitHubModelsClient(github_token)
        
        # Test different types of prompts
        test_cases = [
            {
                "name": "Creative Writing",
                "prompt": "Write a haiku about stars",
                "max_tokens": 50
            },
            {
                "name": "Technical Explanation", 
                "prompt": "Explain what a black hole is in simple terms",
                "max_tokens": 100
            },
            {
                "name": "Code Generation",
                "prompt": "Write a Python function to calculate factorial",
                "max_tokens": 150
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 Test: {test_case['name']}")
            print(f"📝 Prompt: {test_case['prompt']}")
            
            try:
                start_time = datetime.now()
                response = await client.chat_completion(
                    messages=[{"role": "user", "content": test_case['prompt']}],
                    temperature=0.7,
                    max_tokens=test_case['max_tokens']
                )
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                print(f"⏱️ Response Time: {response_time:.2f}s")
                print(f"💬 Response: {response.content[:200]}{'...' if len(response.content) > 200 else ''}")
                print("✅ Test passed")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced test setup error: {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 Astra Bot - GitHub Models Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run basic tests
    basic_success = await test_github_models()
    
    if basic_success:
        print("\n" + "=" * 60)
        # Run advanced tests
        advanced_success = await test_advanced_features()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Basic Tests: {'✅ PASSED' if basic_success else '❌ FAILED'}")
        print(f"Advanced Tests: {'✅ PASSED' if advanced_success else '❌ FAILED'}")
        
        if basic_success and advanced_success:
            print("\n🎉 ALL TESTS PASSED! GitHub Models integration is ready!")
            print("🚀 Ready for deployment to Railway!")
            return True
        else:
            print("\n⚠️ Some tests failed. Check configuration.")
            return False
    else:
        print("\n❌ Basic tests failed. Check your setup.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
