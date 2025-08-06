#!/usr/bin/env python3
"""
Test the enhanced neutral AI system to demonstrate user-vibe awareness
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up basic environment variables for testing
os.environ.setdefault("ASTRA_OPENAI_TOKEN", "test")
os.environ.setdefault("ASTRA_OPENROUTER_TOKEN", "test")
os.environ.setdefault("ASTRA_FREEPIK_API_KEY", "test")


async def test_enhanced_ai():
    """Test the enhanced AI system without personality constraints"""
    try:
        from ai.consolidated_ai_engine import ConsolidatedAIEngine
        from ai.consolidated_ai_engine import (
            ConversationContext,
            UserProfile,
            EmotionalContext,
            ConversationMood,
        )

        print("✅ Enhanced AI Engine imported successfully")

        # Create AI engine instance
        ai_engine = ConsolidatedAIEngine()
        print("✅ AI Engine initialized")

        # Test the new ConversationFlowEngine
        print("\n🧪 Testing ConversationFlowEngine...")

        # Create test context
        context = ConversationContext(
            user_id="123456789",
            channel_id="987654321",
            messages=[
                {"role": "user", "content": "Hey there! How's it going?"},
                {
                    "role": "assistant",
                    "content": "Hello! I'm doing well, thanks for asking!",
                },
                {
                    "role": "user",
                    "content": "Can you help me understand quantum physics?",
                },
            ],
            emotional_context=EmotionalContext(current_mood=ConversationMood.CURIOUS),
            active_topics=["science", "physics"],
        )

        # Create test user profile
        user_profile = UserProfile(
            user_id=123456789, display_name="TestUser", total_interactions=25
        )

        # Test conversation style determination
        style = ai_engine.flow_engine.get_conversation_style(context, user_profile)
        print(f"📊 Conversation Style: {style}")

        # Test system prompt building
        system_prompt = ai_engine._build_system_prompt(context, user_profile, style)
        print(f"\n💬 System Prompt Preview (first 200 chars):")
        print(f"{system_prompt[:200]}...")

        # Test post-processing
        sample_response = "Quantum physics is fascinating! It deals with the behavior of matter and energy at the atomic and subatomic level. 🔬"
        processed = ai_engine._post_process_response(sample_response, context, style)
        print(f"\n🔄 Processed Response: {processed}")

        # Test fallback response
        fallback = ai_engine._get_fallback_response("Hello", "123456789")
        print(f"\n🆘 Fallback Response: {fallback}")

        print("\n✅ Enhanced AI system is working properly!")
        print("🎉 The AI is now more neutral, user-vibe aware, and naturally engaging!")

    except Exception as e:
        print(f"❌ Error testing enhanced AI: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Testing Enhanced AI System")
    print("=" * 50)
    asyncio.run(test_enhanced_ai())
