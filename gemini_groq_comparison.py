#!/usr/bin/env python3
"""
Gemini vs Groq Comparative Efficiency Analysis
"""
import asyncio
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


class GeminiGroqComparison:
    """Compare Gemini and Groq performance side by side"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "gemini_results": {},
            "groq_results": {},
            "comparison": {},
        }

    async def test_provider_efficiency(self, provider_name, test_prompts):
        """Test a specific provider's efficiency"""
        print(f"\n🔬 TESTING {provider_name.upper()} EFFICIENCY")
        print("-" * 50)

        try:
            if provider_name == "gemini":
                from ai.google_gemini_client import GoogleGeminiClient

                client = GoogleGeminiClient()
                if not client.available:
                    return None
                generate_func = client.generate_response
            elif provider_name == "groq":
                from ai.multi_provider_ai import MultiProviderAIManager, AIProvider

                manager = MultiProviderAIManager()
                groq_status = manager.providers.get(AIProvider.GROQ)
                if not groq_status or not groq_status.available:
                    return None
                generate_func = manager._generate_groq_response

            results = []

            for i, prompt in enumerate(test_prompts, 1):
                print(f"📝 Test {i}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

                start_time = time.time()

                try:
                    if provider_name == "gemini":
                        response = await generate_func(
                            prompt=prompt, max_tokens=300, temperature=0.7
                        )
                        content = response.get("content", "")
                        model = response.get("model", "unknown")
                        tokens = response.get("usage", {}).get("total_tokens", 0)
                    else:  # groq
                        response = await generate_func(
                            prompt=prompt, max_tokens=300, temperature=0.7
                        )
                        content = response.content
                        model = response.model
                        tokens = response.usage.get("total_tokens", 0)

                    response_time = time.time() - start_time

                    print(f"✅ Response received ({response_time:.2f}s)")
                    print(f"   Model: {model}")
                    print(f"   Length: {len(content)} chars")
                    print(f"   Tokens: {tokens}")
                    print(
                        f"   Preview: {content[:80]}{'...' if len(content) > 80 else ''}"
                    )

                    results.append(
                        {
                            "prompt": prompt,
                            "response_time": response_time,
                            "content_length": len(content),
                            "tokens_used": tokens,
                            "model": model,
                            "success": True,
                            "content": content,
                        }
                    )

                except Exception as e:
                    response_time = time.time() - start_time
                    print(f"❌ Failed ({response_time:.2f}s): {e}")
                    results.append(
                        {
                            "prompt": prompt,
                            "response_time": response_time,
                            "success": False,
                            "error": str(e),
                        }
                    )

            return results

        except Exception as e:
            print(f"❌ {provider_name} test failed: {e}")
            return None

    async def run_comparative_test(self):
        """Run side-by-side comparison"""
        print("⚖️ GEMINI vs GROQ EFFICIENCY COMPARISON")
        print("=" * 70)

        # Test prompts for comparison
        test_prompts = [
            "What is 25 * 8?",
            "Explain quantum computing in one paragraph.",
            "Write a welcome message for AstraBot users.",
            "What are the benefits of using Discord bots?",
            "Generate a Python function to calculate fibonacci numbers.",
        ]

        # Test both providers
        print("🧪 Testing both providers with identical prompts...")

        gemini_results = await self.test_provider_efficiency("gemini", test_prompts)
        groq_results = await self.test_provider_efficiency("groq", test_prompts)

        self.results["gemini_results"] = gemini_results
        self.results["groq_results"] = groq_results

        # Analyze results
        self.analyze_comparison()

    def analyze_comparison(self):
        """Analyze and compare the results"""
        print("\n📊 COMPARATIVE ANALYSIS")
        print("=" * 70)

        gemini_data = self.results["gemini_results"]
        groq_data = self.results["groq_results"]

        if not gemini_data or not groq_data:
            print("❌ Cannot compare - insufficient data")
            return

        # Filter successful tests
        gemini_success = [r for r in gemini_data if r.get("success", False)]
        groq_success = [r for r in groq_data if r.get("success", False)]

        if not gemini_success or not groq_success:
            print("❌ Cannot compare - no successful tests")
            return

        # Calculate metrics
        metrics = {}

        # Gemini metrics
        gemini_avg_time = sum(r["response_time"] for r in gemini_success) / len(
            gemini_success
        )
        gemini_avg_length = sum(r["content_length"] for r in gemini_success) / len(
            gemini_success
        )
        gemini_avg_tokens = (
            sum(r["tokens_used"] for r in gemini_success) / len(gemini_success)
            if any(r["tokens_used"] for r in gemini_success)
            else 0
        )
        gemini_success_rate = len(gemini_success) / len(gemini_data) * 100

        # Groq metrics
        groq_avg_time = sum(r["response_time"] for r in groq_success) / len(
            groq_success
        )
        groq_avg_length = sum(r["content_length"] for r in groq_success) / len(
            groq_success
        )
        groq_avg_tokens = (
            sum(r["tokens_used"] for r in groq_success) / len(groq_success)
            if any(r["tokens_used"] for r in groq_success)
            else 0
        )
        groq_success_rate = len(groq_success) / len(groq_data) * 100

        # Comparison table
        print("📋 PERFORMANCE COMPARISON TABLE")
        print("-" * 70)
        print(f"{'Metric':<25} {'Gemini':<20} {'Groq':<20} {'Winner':<10}")
        print("-" * 70)

        # Success Rate
        success_winner = (
            "Gemini"
            if gemini_success_rate > groq_success_rate
            else "Groq" if groq_success_rate > gemini_success_rate else "Tie"
        )
        print(
            f"{'Success Rate':<25} {gemini_success_rate:.1f}%{'':<15} {groq_success_rate:.1f}%{'':<15} {success_winner:<10}"
        )

        # Response Time (lower is better)
        time_winner = (
            "Gemini"
            if gemini_avg_time < groq_avg_time
            else "Groq" if groq_avg_time < gemini_avg_time else "Tie"
        )
        print(
            f"{'Avg Response Time':<25} {gemini_avg_time:.2f}s{'':<14} {groq_avg_time:.2f}s{'':<14} {time_winner:<10}"
        )

        # Content Length (more comprehensive)
        length_winner = (
            "Gemini"
            if gemini_avg_length > groq_avg_length
            else "Groq" if groq_avg_length > gemini_avg_length else "Tie"
        )
        print(
            f"{'Avg Content Length':<25} {gemini_avg_length:.0f} chars{'':<10} {groq_avg_length:.0f} chars{'':<10} {length_winner:<10}"
        )

        # Token Efficiency
        if gemini_avg_tokens > 0 and groq_avg_tokens > 0:
            token_winner = (
                "Gemini"
                if gemini_avg_tokens < groq_avg_tokens
                else "Groq" if groq_avg_tokens < gemini_avg_tokens else "Tie"
            )
            print(
                f"{'Avg Tokens Used':<25} {gemini_avg_tokens:.0f}{'':<15} {groq_avg_tokens:.0f}{'':<15} {token_winner:<10}"
            )

        print("-" * 70)

        # Overall assessment
        print("\n🏆 OVERALL ASSESSMENT")
        print("-" * 50)

        # Speed comparison
        if gemini_avg_time < groq_avg_time:
            speed_diff = ((groq_avg_time - gemini_avg_time) / groq_avg_time) * 100
            print(f"⚡ Speed: Gemini is {speed_diff:.1f}% faster than Groq")
        elif groq_avg_time < gemini_avg_time:
            speed_diff = ((gemini_avg_time - groq_avg_time) / gemini_avg_time) * 100
            print(f"⚡ Speed: Groq is {speed_diff:.1f}% faster than Gemini")
        else:
            print("⚡ Speed: Both providers have similar response times")

        # Content comparison
        if gemini_avg_length > groq_avg_length:
            length_diff = (
                (gemini_avg_length - groq_avg_length) / groq_avg_length
            ) * 100
            print(
                f"📝 Content: Gemini provides {length_diff:.1f}% more comprehensive responses"
            )
        elif groq_avg_length > gemini_avg_length:
            length_diff = (
                (groq_avg_length - gemini_avg_length) / gemini_avg_length
            ) * 100
            print(
                f"📝 Content: Groq provides {length_diff:.1f}% more comprehensive responses"
            )
        else:
            print("📝 Content: Both providers give similar response lengths")

        # Reliability
        if gemini_success_rate > groq_success_rate:
            print(
                f"🛡️ Reliability: Gemini has higher success rate ({gemini_success_rate:.1f}% vs {groq_success_rate:.1f}%)"
            )
        elif groq_success_rate > gemini_success_rate:
            print(
                f"🛡️ Reliability: Groq has higher success rate ({groq_success_rate:.1f}% vs {gemini_success_rate:.1f}%)"
            )
        else:
            print("🛡️ Reliability: Both providers have excellent reliability")

        # Models used
        gemini_models = set(r["model"] for r in gemini_success)
        groq_models = set(r["model"] for r in groq_success)

        print(f"\n🤖 Models Used:")
        print(f"   Gemini: {', '.join(gemini_models)}")
        print(f"   Groq: {', '.join(groq_models)}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if gemini_avg_time < groq_avg_time and gemini_success_rate >= groq_success_rate:
            print(
                "   🎯 Gemini excels in speed and reliability - ideal for real-time responses"
            )
            print(
                "   🎯 Groq provides good alternative with different model capabilities"
            )
        elif (
            groq_avg_time < gemini_avg_time and groq_success_rate >= gemini_success_rate
        ):
            print(
                "   🎯 Groq excels in speed and reliability - ideal for real-time responses"
            )
            print(
                "   🎯 Gemini provides good alternative with different model capabilities"
            )
        else:
            print("   🎯 Both providers are excellent - use based on specific needs")
            print("   🎯 Fallback system ensures high availability")

        # Store comparison results
        self.results["comparison"] = {
            "gemini_metrics": {
                "avg_response_time": gemini_avg_time,
                "avg_content_length": gemini_avg_length,
                "avg_tokens": gemini_avg_tokens,
                "success_rate": gemini_success_rate,
            },
            "groq_metrics": {
                "avg_response_time": groq_avg_time,
                "avg_content_length": groq_avg_length,
                "avg_tokens": groq_avg_tokens,
                "success_rate": groq_success_rate,
            },
            "winners": {
                "speed": time_winner,
                "content": length_winner,
                "reliability": success_winner,
            },
        }

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_groq_comparison_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Detailed comparison saved to: {filename}")


async def main():
    """Run the comparative analysis"""
    comparison = GeminiGroqComparison()
    await comparison.run_comparative_test()
    print("\n🎉 Comparative analysis completed!")


if __name__ == "__main__":
    asyncio.run(main())
