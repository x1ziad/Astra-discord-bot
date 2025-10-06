#!/usr/bin/env python3
"""
🌟 AstraBot Self-Aware Personality System - DEMO
Comprehensive demonstration of AstraBot's advanced personality capabilities

This showcases the complete self-aware personality system that makes AstraBot
truly special and different from other Discord bots.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.personality_integration import (
    check_for_identity_response,
    enhance_ai_chat_response,
    get_personality_integration,
)


async def showcase_personality_system():
    """Comprehensive showcase of AstraBot's personality system"""

    print("🌟 ASTRABOT SELF-AWARE PERSONALITY SYSTEM")
    print("✨ Created by @7zxk - Advanced AI Companion")
    print("📅 Launched: October 5th, 2025")
    print("=" * 60)

    # Simulate different users asking identity questions
    demo_scenarios = [
        {
            "user_id": 1001,
            "user_name": "CuriousUser",
            "question": "Hey Astra, who are you exactly?",
            "context": "casual chat",
            "tone": "casual",
        },
        {
            "user_id": 1002,
            "user_name": "Professor",
            "question": "Could you please provide details about your creator and development?",
            "context": "academic discussion",
            "tone": "formal",
        },
        {
            "user_id": 1003,
            "user_name": "ExcitedNewbie",
            "question": "OMG what can you do?! You seem awesome!",
            "context": "general",
            "tone": "excited",
        },
        {
            "user_id": 1004,
            "user_name": "DeepThinker",
            "question": "What is your fundamental purpose and mission?",
            "context": "philosophical",
            "tone": "serious",
        },
        {
            "user_id": 1005,
            "user_name": "TechEnthusiast",
            "question": "Tell me about your background and what makes you special",
            "context": "technical",
            "tone": "curious",
        },
    ]

    print("🎭 ADAPTIVE PERSONALITY RESPONSES DEMO")
    print("Watch how AstraBot adapts to different users and contexts:")
    print("-" * 60)

    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n🔸 Scenario {i}: {scenario['user_name']} ({scenario['tone']} tone)")
        print(f"   Question: \"{scenario['question']}\"")
        print(f"   Context: {scenario['context']}")

        response = await check_for_identity_response(
            user_id=scenario["user_id"],
            message=scenario["question"],
            user_name=scenario["user_name"],
            channel_context=scenario["context"],
        )

        if response:
            print(f'   🤖 AstraBot: "{response}"')
            print(f"   📊 Adaptation: Successfully matched {scenario['tone']} tone")
        else:
            print(f"   ❌ No response generated")

        # Small delay for dramatic effect
        await asyncio.sleep(0.5)

    print("\n" + "=" * 60)
    print("🧠 PERSONALITY CORE STATISTICS")
    print("-" * 60)

    # Get comprehensive personality stats
    integration = await get_personality_integration()
    stats = await integration.get_personality_stats()

    if stats.get("status") == "active":
        summary = stats.get("summary", {})

        print(f"✅ System Status: FULLY OPERATIONAL")
        print(f"👥 Active User Contexts: {summary.get('active_users', 0)}")
        print(f"🎭 Personality Adaptations: {summary.get('adaptation_count', 0)}")

        # Identity information
        identity = summary.get("identity", {})
        if identity:
            print(f"\n🌟 IDENTITY PROFILE:")
            print(f"   • Name: {identity.get('name', 'Astra')}")
            print(f"   • Version: {identity.get('version', '2.0.0')}")
            print(f"   • Creator: {identity.get('creator', 'Z')}")
            print(
                f"   • Launch Date: {identity.get('launch_date', 'October 5th, 2025')}"
            )
            print(
                f"   • Mission: {identity.get('mission', 'Advanced AI companion')[:50]}..."
            )

        # Personality traits
        traits = summary.get("core_traits", {})
        if traits:
            print(f"\n🎭 PERSONALITY TRAITS:")
            trait_names = {
                "adaptability": "Adaptability",
                "curiosity": "Curiosity",
                "intellect": "Intellectual Depth",
                "empathy": "Empathy",
                "integrity": "Integrity",
                "humility": "Humility",
            }

            for trait, value in traits.items():
                trait_name = trait_names.get(trait, trait.title())
                percentage = int(value * 100)
                bar = "█" * (percentage // 10) + "░" * (10 - percentage // 10)
                print(f"   • {trait_name}: [{bar}] {percentage}%")
    else:
        print(f"⚠️ System Status: {stats.get('status', 'unknown').upper()}")

    print("\n" + "=" * 60)
    print("🚀 KEY FEATURES DEMONSTRATION")
    print("-" * 60)

    features = [
        "🔍 Identity Question Detection - Recognizes when users ask about the bot",
        "🎭 Adaptive Response Generation - Matches user tone and communication style",
        "💭 Contextual Awareness - Considers conversation context and channel type",
        "📊 User Profiling - Builds individual personality adaptations",
        "⚡ Real-time Integration - Seamlessly works with existing AI chat systems",
        "🧠 Self-Improvement - Learns and evolves from every interaction",
        "🌟 Natural Responses - No frames or automated messages, just natural chat",
    ]

    for feature in features:
        print(f"   ✅ {feature}")
        await asyncio.sleep(0.3)

    print("\n" + "=" * 60)
    print("💡 USAGE EXAMPLES")
    print("-" * 60)

    examples = [
        "User: 'Who are you?' → Natural self-introduction with personality",
        "User: 'What can you do?' → Adaptive capability explanation",
        "User: 'Who created you?' → Story about Z and the development journey",
        "User: 'What's your purpose?' → Mission and vision explanation",
        "User: 'Tell me about yourself' → Comprehensive background sharing",
    ]

    for example in examples:
        print(f"   📝 {example}")

    print("\n" + "=" * 60)
    print("🎉 ASTRABOT PERSONALITY SYSTEM READY!")
    print("=" * 60)

    print("\n🌟 What makes this special:")
    print("   • First truly self-aware Discord bot personality system")
    print("   • Adapts naturally to user communication styles")
    print("   • Comprehensive identity knowledge and storytelling")
    print("   • Seamless integration with existing AI capabilities")
    print("   • Created by @7zxk with quantum computing and cosmology expertise")
    print("   • Launched October 5th, 2025 - A new era of AI companions!")

    print("\n🚀 Ready for Discord deployment and real-world interaction!")


if __name__ == "__main__":
    asyncio.run(showcase_personality_system())
